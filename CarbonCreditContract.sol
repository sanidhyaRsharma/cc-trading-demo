pragma solidity >=0.4.24 <0.6.0;
pragma experimental ABIEncoderV2;

contract ReceiverPays {
    address certifying_owner;
    uint256 uuid = 0;
    struct CarbonCredit {
        uint256 uuid;
        address owner_addr;
        address certifying_auth_addr;
        uint256 ttl;
        bool retired;
    }

    mapping(uint256 => bool) usedNonces;
    mapping(address => uint256[]) possessedCC;
    //mapping(uint256 => uint256[]) timemap;
    CarbonCredit[] CCList;
    constructor() public {
        certifying_owner = msg.sender;
    }

    function getCCListCount() public view returns (uint256) {
        return CCList.length;
    }

    function getUUID() public view returns (uint256) {
        return uuid;
    }

    function incUUID() public {
        uuid++;
    }

    function getCarbonCredit(uint256 id) public view returns (CarbonCredit memory) {
        return CCList[id];
    }

    function retireCredit(uint256 uuid) public {
        //require(now >= );
        CCList[uuid].retired = true;
    }

    function retireCreditList(uint256[] memory uuid_list) public {
        for (uint i = 0; i < uuid_list.length; i++)
            retireCredit(uuid_list[i]);
    }

    function getBalanceCount() public view returns(uint count) {
        return possessedCC[msg.sender].length;
    }

    function getCurrentBalanceNow() public view returns (uint){
        uint balance = 0;
        uint len = getBalanceCount();
        for (uint i = 0; i < len; i++) {
            if (CCList[possessedCC[msg.sender][i]].retired == false)
                balance += 1;
        }
        return balance;
    }

    function addCredit(string memory verified_certificate, address owner, uint256 amount, uint256 ttl) public payable returns (uint256, uint256) {
        require(msg.sender == certifying_owner);
        require(amount > 0);
        require(ttl > 0);
        ttl = ttl + now;
        //ttl > ttl + now);
        int256 uuid_start = -1;
        for (uint256 i = 0; i < amount; i++) {
            uint256 uuid_tmp = getUUID();
            if (uuid_start == -1)
                uuid_start = int256(uuid_tmp);
            CCList.push(CarbonCredit(
                uuid_tmp,
                owner,
                certifying_owner,
                ttl,
                false
            ));
            possessedCC[owner].push(uuid_tmp);
            //timemap[ttl].push(uuid_tmp);
            incUUID();
        }
        return (uint256(uuid_start), ttl);
    }
}