
import unittest
from pathlib import Path
from src.ethbmc import EthBMC
from src.utils.solidity_parser import SolidityParser

class TestEthBMC(unittest.TestCase):
    def setUp(self):
        self.checker = EthBMC()
        self.parser = SolidityParser()
        
    def test_overflow_detection(self):
        """Test arithmetic overflow detection"""
        contract = """
        pragma solidity ^0.8.0;
        
        contract Test {
            uint256 public value;
            
            function unsafeAdd(uint256 a) public {
                value += a;  // Potential overflow
            }
        }
        """
        
        # Create temporary contract file
        test_dir = Path("tests/temp")
        test_dir.mkdir(exist_ok=True)
        contract_path = test_dir / "overflow_test.sol"
        
        with open(contract_path, "w") as f:
            f.write(contract)
            
        result = self.checker.check_contract(str(contract_path))
        self.assertFalse(result["overflow"])
        
    def test_reentrancy_detection(self):
        """Test reentrancy vulnerability detection"""
        contract = """
        pragma solidity ^0.8.0;
        
        contract Test {
            mapping(address => uint) public balances;
            
            function withdraw() public {
                uint balance = balances[msg.sender];
                (bool success, ) = msg.sender.call{value: balance}("");
                balances[msg.sender] = 0;
            }
        }
        """
        
        test_dir = Path("tests/temp")
        test_dir.mkdir(exist_ok=True)
        contract_path = test_dir / "reentrancy_test.sol"
        
        with open(contract_path, "w") as f:
            f.write(contract)
            
        result = self.checker.check_contract(str(contract_path))
        self.assertFalse(result["reentrancy"])
        
    def test_access_control(self):
        """Test access control vulnerability detection"""
        contract = """
        pragma solidity ^0.8.0;
        
        contract Test {
            uint256 public value;
            
            function setValue(uint256 newValue) public {
                value = newValue;  // Missing access control
            }
        }
        """
        
        test_dir = Path("tests/temp")
        test_dir.mkdir(exist_ok=True)
        contract_path = test_dir / "access_test.sol"
        
        with open(contract_path, "w") as f:
            f.write(contract)
            
        result = self.checker.check_contract(str(contract_path))
        self.assertFalse(result["access_control"])
        
    def test_benchmark_analysis(self):
        """Test full benchmark analysis"""
        # Create test benchmarks
        benchmark_dir = Path("tests/temp/benchmarks")
        benchmark_dir.mkdir(exist_ok=True)
        
        # Create test contracts
        for i in range(3):
            contract = f"""
            pragma solidity ^0.8.0;
            
            contract Test{i} {{
                uint256 public value;
                
                function setValue(uint256 newValue) public {{
                    value = newValue;
                }}
            }}
            """
            
            with open(benchmark_dir / f"test_{i}.sol", "w") as f:
                f.write(contract)
        
        results = self.checker.analyze_benchmarks()
        self.assertEqual(len(results), 3)
        
    def tearDown(self):
        """Clean up temporary test files"""
        import shutil
        test_dir = Path("tests/temp")
        if test_dir.exists():
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    unittest.main()