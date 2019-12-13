pragma solidity ^0.5.1;

contract CarbonCreditContract{
    
    uint256 uuid;
    struct CarbonCredit {
        uint256 private uid;
        string private current_owner;
        uint256 private expiry_time;
        string private cert_authority;
        bool private is_with_generator;
        string private json_certificate;
    }
    
    //Create mapping of credits to owners
    private CarbonCreditContract[] creditsList;
    
    //Add carbon credit certificate to creditsList
    function addCredit(string _owner, uint256 _time, string _cert_authority, string _certificate) public returns(bool){
        //timer expired condition
        //check if certificate authority exists in list of certified authorities
        //verify digital signature
        //add credit to creditsList
    }
    
    //Change owner of credit certificate
    function transferCredit(uint256 _uid, string _current_owner, string _new_owner){
        //Check if current_owner not retired
        //Check if msg.sender == owner 
    }
    
    //Change owner to "retired" so as to make it unusable
    function retireCredit(uint256 _uid){
        //Check time.now > expiry_time
        
    }
    
    //Generates unique integers for id of carbon credit
    function getUID() public returns uint{
        return uuid++;
    }
}