// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract logger{
    event messageLog(string msg);
    function logmessage(string memory text) public returns (bool){
        emit messageLog(text);
        return true;
    }
}