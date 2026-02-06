// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/MockUSDC.sol";
import "../src/QuestEscrowManager.sol";
import "../src/QuestDisputeManager.sol";

contract DeployLocal is Script {
    function run() external {
        address admin = vm.envAddress("ADMIN_ADDRESS");
        address creator = vm.envAddress("CREATOR_ADDRESS");
        address operatorAddr = vm.envAddress("OPERATOR_ADDRESS");

        vm.startBroadcast();

        MockUSDC usdc = new MockUSDC();
        QuestEscrowManager escrow = new QuestEscrowManager(admin, address(usdc));
        QuestDisputeManager dispute = new QuestDisputeManager(admin);

        escrow.setDisputeManager(address(dispute));
        dispute.setEscrowManager(address(escrow));

        escrow.grantRole(escrow.OPERATOR_ROLE(), admin);
        escrow.grantRole(escrow.OPERATOR_ROLE(), operatorAddr);
        escrow.grantRole(escrow.OPERATOR_ROLE(), address(dispute));

        dispute.grantRole(dispute.OPERATOR_ROLE(), admin);
        dispute.grantRole(dispute.OPERATOR_ROLE(), operatorAddr);
        dispute.grantRole(dispute.OPERATOR_ROLE(), address(escrow));

        usdc.mint(creator, 1_000_000e6);
        vm.stopBroadcast();

        console2.log("MockUSDC:", address(usdc));
        console2.log("Escrow:", address(escrow));
        console2.log("Dispute:", address(dispute));
    }
}
