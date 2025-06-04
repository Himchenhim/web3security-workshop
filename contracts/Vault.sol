// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "wake/console.sol";


// possibly adding pause
// possibly adding withdrawal delay

/**
 * @title SingleTokenVault
 * @dev A vault contract that manages deposits and withdrawals for a single ERC20 token
 */
contract SingleTokenVault is Ownable {
    // Custom Errors
    error InvalidToken();
    error InvalidDepositLimits();
    error BelowMinDeposit();
    error AboveMaxDeposit();
    error TransferFailed();
    error InsufficientBalance();
    error ZeroAmount();

    IERC20 public immutable token;

    // User address => balance
    mapping(address => uint256) private _balances;

    uint256 public maxDepositAmount;
    uint256 public minDepositAmount;
    uint256 public totalDeposits;

    // Events
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event DepositLimitsUpdated(uint256 minAmount, uint256 maxAmount);

    constructor(
        address _token,
        uint256 _minDepositAmount,
        uint256 _maxDepositAmount
    ) Ownable(msg.sender) {
        if (_token == address(0)) revert InvalidToken();
        if (_maxDepositAmount <= _minDepositAmount) revert InvalidDepositLimits();

        token = IERC20(_token);
        minDepositAmount = _minDepositAmount;
        maxDepositAmount = _maxDepositAmount;
    }

    /**
     * @dev Deposits tokens into the vault
     * @param amount The amount of tokens to deposit
     */
    function deposit(uint256 amount) external {
        if (amount == 0) revert ZeroAmount();
        if (amount < minDepositAmount) revert BelowMinDeposit();
        if (amount > maxDepositAmount) revert AboveMaxDeposit();


        bool success = token.transferFrom(msg.sender, address(this), amount);
        if (!success) revert TransferFailed();

        _balances[msg.sender] += amount;
        totalDeposits += amount;

        emit Deposited(msg.sender, amount);
    }

    /**
     * @dev Withdraws tokens from the vault
     * @param amount The amount of tokens to withdraw
     */
    function withdraw(uint256 amount) external {
        if (amount == 0) revert ZeroAmount();
        if (_balances[msg.sender] < amount) revert InsufficientBalance();

        _balances[msg.sender] -= amount;
        totalDeposits -= amount;

        bool success = token.transfer(msg.sender, amount);
        if (!success) revert TransferFailed();

        emit Withdrawn(msg.sender, amount);
    }

    /**
     * @dev Returns the balance of a user
     * @param user The user address
     */
    function balanceOf(address user) external view returns (uint256) {
        return _balances[user];
    }

    /**
     * @dev Updates deposit limits (only owner)
     */
    function setDepositLimits(uint256 _minAmount, uint256 _maxAmount) external onlyOwner {
        if (_maxAmount <= _minAmount) revert InvalidDepositLimits();
        minDepositAmount = _minAmount;
        maxDepositAmount = _maxAmount;
        emit DepositLimitsUpdated(_minAmount, _maxAmount);
    }

}