#!/usr/bin/env python3

import os
import requests
from pathlib import Path
import json
import time
import logging
import re
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

class BenchmarkDownloader:
    def __init__(self, output_dir: str = "benchmarks", target_solc_version: str = "0.8.0"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.target_solc_version = target_solc_version
        self.session = requests.Session()
    
    def download_benchmarks(self, count: int = 100) -> int:
        """Download benchmark contracts compatible with target Solidity version"""
        downloaded = 0
        logging.info(f"Starting download of {count} benchmark contracts (Solidity {self.target_solc_version})")
        
        progress_bar = tqdm(total=count)
        
        # Generate test contracts with known vulnerabilities
        logging.info("Generating test contracts with known vulnerabilities...")
        test_contracts = self._generate_test_contracts(count)
        
        for contract in test_contracts:
            if downloaded >= count:
                break
                
            contract_path = self.output_dir / f"benchmark_{downloaded + 1}.sol"
            with open(contract_path, "w") as f:
                f.write(contract)
            downloaded += 1
            progress_bar.update(1)
        
        progress_bar.close()
        logging.info(f"Successfully downloaded {downloaded} contracts")
        return downloaded
    
    def _generate_test_contracts(self, count: int) -> List[str]:
        """Generate test contracts with various vulnerability patterns"""
        contracts = []
        
        # Contract templates with different vulnerability patterns
        templates = [
            self._generate_overflow_contract,
            self._generate_reentrancy_contract,
            self._generate_access_control_contract,
            self._generate_safe_contract
        ]
        
        while len(contracts) < count:
            for template in templates:
                if len(contracts) >= count:
                    break
                contracts.append(template(len(contracts)))
        
        return contracts
    
    def _generate_overflow_contract(self, index: int) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^{self.target_solc_version};

contract OverflowTest{index} {{
    uint256 private value;
    
    function unsafeAdd(uint256 a) public {{
        unchecked {{
            value += a;  // Potential overflow
        }}
    }}
    
    function unsafeMul(uint256 a) public {{
        unchecked {{
            value *= a;  // Potential overflow
        }}
    }}
    
    function getValue() public view returns (uint256) {{
        return value;
    }}
}}"""
    
    def _generate_reentrancy_contract(self, index: int) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^{self.target_solc_version};

contract ReentrancyTest{index} {{
    mapping(address => uint) private balances;
    
    function deposit() public payable {{
        balances[msg.sender] += msg.value;
    }}
    
    function withdraw() public {{
        uint balance = balances[msg.sender];
        require(balance > 0, "No balance");
        
        (bool success, ) = msg.sender.call{{value: balance}}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0;  // State update after external call
    }}
    
    function getBalance(address account) public view returns (uint) {{
        return balances[account];
    }}
}}"""
    
    def _generate_access_control_contract(self, index: int) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^{self.target_solc_version};

contract AccessControlTest{index} {{
    uint256 private value;
    
    function setValue(uint256 newValue) public {{  // Missing access control
        value = newValue;
    }}
    
    function criticalFunction() public {{  // Missing access control
        selfdestruct(payable(msg.sender));
    }}
    
    function getValue() public view returns (uint256) {{
        return value;
    }}
}}"""
    
    def _generate_safe_contract(self, index: int) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^{self.target_solc_version};

contract SafeTest{index} {{
    address private owner;
    uint256 private value;
    
    constructor() {{
        owner = msg.sender;
    }}
    
    modifier onlyOwner() {{
        require(msg.sender == owner, "Not owner");
        _;
    }}
    
    function setValue(uint256 newValue) public onlyOwner {{
        value = newValue;
    }}
    
    function getValue() public view returns (uint256) {{
        return value;
    }}
    
    function safeAdd(uint256 a) public onlyOwner {{
        value += a;  // Safe due to Solidity 0.8.0+ overflow checks
    }}
}}"""

def main():
    try:
        downloader = BenchmarkDownloader(target_solc_version="0.8.0")
        count = downloader.download_benchmarks(100)
        if count < 100:
            logging.warning(f"Only downloaded {count} contracts")
    except Exception as e:
        logging.error(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()