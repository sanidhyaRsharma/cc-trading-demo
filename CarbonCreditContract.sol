pragma solidity >=0.4.24 <0.6.0;
pragma experimental ABIEncoderV2;

contract ReceiverPays {
    address certifying_owner;
    uint256 uuid = 0;
    event addEvent (uint256 uuid);
    event retireEvent (bool isChanged);
    struct CarbonCredits {
        uint256 uuid;
        address owner_addr;
        address certifying_auth_addr;
        uint256 amount;
        uint256 ttl;
        string certi_hash;
        bool retired;
    }
    constructor () public{
        certifying_owner = msg.sender;
    }
    mapping (address => CarbonCredits[]) holdings;
    
    /// addCredits to store Carbon Credits
    function addCredits(string memory _certi_hash, address _owner_address, uint256 _amount, uint256 _ttl ) public payable returns (uint256){
        require(msg.sender == certifying_owner);
        incUUID();
        holdings[_owner_address].push(CarbonCredits(uuid, _owner_address, certifying_owner, _amount, _ttl + now, _certi_hash, false));
        emit addEvent(uuid);
        return uuid;
    }
    
    // transferCredits to transfer Carbon Credits
    function transferCredits(address _owner_address, address _receiver_address, uint256 _uuid, uint256 _amount) public payable {
        require(msg.sender == _owner_address);
        bool txDone = false;
        for(uint256 i = 0; i < holdings[_owner_address].length; i++){
            if(holdings[_owner_address][i].uuid == _uuid && (holdings[_owner_address][i].amount >= _amount)){
                
                require(holdings[_owner_address][i].retired == false);
                CarbonCredits memory copyOfCredits = holdings[_owner_address][i];
                holdings[_receiver_address].push(CarbonCredits(copyOfCredits.uuid, _receiver_address, copyOfCredits.certifying_auth_addr, _amount, copyOfCredits.ttl, copyOfCredits.certi_hash, copyOfCredits.retired));
                holdings[_owner_address][i].amount -= _amount;
                if (holdings[_owner_address][i].amount == 0){
                    delete holdings[_owner_address][i];    
                }
                txDone = true;
                break;
            }
        }
        require(txDone== true);
    }
    
    // retireCredits to retire Carbon Credits
    function retireCredits(address _address) public payable returns(bool){
        bool isChanged = false;
        for(uint256 i = 0; i< holdings[_address].length; i++){
            if (now> holdings[_address][i].ttl && holdings[_address][i].retired == false){
                holdings[_address][i].retired = true;
                isChanged = true;
            }
        }
        emit retireEvent(isChanged);
        return isChanged;
    }
    
    function viewCurrentBalance(address _address) public view returns (uint256){
       uint256 balance = 0;
       for(uint256 i = 0; i < holdings[_address].length; i++) {
           if(holdings[_address][i].retired == false){
                balance += holdings[_address][i].amount;
           }
       }
       return balance;
    }
    
    function incUUID() private{
        uuid+=1;
    }
}