pragma solidity ^0.8.0;


contract NewsDetection {

    struct News{
        address immutable author;
        string immutable title;
        string immutable body;
        string[] immutable topics;
        bytes32 immutable newsId;
        uint immutable timestamp;
    }

    struct Vote {
        Voter voter;
        bool voteValue;
    }

    struct VoterRating {
        uint numTotalVotes;
        uint numCorrectVotes;
    }

    struct Voter {
        address voter;
        map(string => VoterRating) ratings;
    }

    News immutable news;

    uint constant deposit = 10 ether;
    uint constant NUM_VOTE_THRESHOLD = 100;

    bool detectedAccuracy;
    bool isLocked;
    uint accuracy;
    Vote[] votes;
    uint private totalDeposit;


    constructor(address _author, string memory _title, string memory _body, string[] memory _topics) {
        news = News({
            author: _author,
            title: _title,
            body: _body,
            topics: _topics,
            newsId: keccak256(abi.encodePacked(_author, _title, _body, block.timestamp)),
            timestamp: block.timestamp
        });
        isLocked = false;
    }
    
    function hasVoted(address _voter) private view returns (bool) {
        for (uint i = 0; i < votes.length; i++) {
            if (votes[i].voter == _voter) {
                return true;
            }
        }
        return false;
    }

    function castVote(Voter _voter, bool _voteValue) public {
        require(!isLocked, "Voting is locked");
        require(!hasVoted(_voter.voter), "Already voted");
        require(msg.value == deposit, "Incorrect deposit amount");

        votes.push(Vote(_voter, _voteValue));
        totalDeposit += deposit;

        if (votes.length >= NUM_VOTE_THRESHOLD) {
            calculateAccuracy();
        }
    }

    function calculateNewsAccuracyTopic(string memory _topic) private view returns (uint[2] memory) {
        uint[2] memory newsAccuraciesTopic;
        uint[2] memory numVotes;
        for (uint i = 0; i < votes.length; i++) {
            if (votes[i].voteValue == true) {
                numVotes[0]++;
                newsAccuraciesTopic[0] += votes[i].voter.ratings[_topic].numCorrectVotes *100 / votes[i].voter.ratings[_topic].numTotalVotes;
            } else {
                numVotes[1]++;
                newsAccuraciesTopic[1] += votes[i].voter.ratings[_topic].numCorrectVotes *100 / votes[i].voter.ratings[_topic].numTotalVotes;
            }
        }
        newsAccuraciesTopic[0] /= numVotes[0]*100;
        newsAccuraciesTopic[1] /= numvotes[1]*100;
        return newsAccuraciesTopic;
    }

    function calculateAccuracy() private {
        uint[2] memory newsAccuracies;
        for (uint i = 0; i < topics.length; i++) {
            uint[2] memory newsAccuraciesTopic = calculateNewsAccuracyTopic(topics[i]);
            newsAccuracies[0] += newsAccuraciesTopic[0];
            newsAccuracies[1] += newsAccuraciesTopic[1];
        }

        uint totalTrueVotes = newsAccuracies[0]*100/length(topics);
        uint totalFalseVotes = newsAccuracies[1]*100/length(topics);
        uint totalVotes = totalTrueVotes + totalFalseVotes;

        require(totalVotes > 0, "No votes cast");

        if (totalTrueVotes > totalFalseVotes ) {
            detectedAccuracy = true;
            accuracy = (totalTrueVotes * 100) / totalVotes;
        } else if (totalFalseVotes > totalTrueVotes ){
            detectedAccuracy = false;
            accuracy = (totalFalseVotes * 100) / totalVotes;
        } else {
            revert("Draw");
        }
        distributeRewards();
        lockVotes();
        recalculateRating();
    }

    function recalculateRating() private {
        for (uint i = 0; i < votes.length; i++) {
            if (votes[i].voteValue == detectedAccuracy) {
                increaseVoterRating(votes[i].voter);
            } else {
                decreaseVoterRating(votes[i].voter);
            }
        }
    }

    function increaseVoterRating(address _voter) private {
        for (uint i = 0; i < news.topics.length; i++) {
            voters[_voter].ratings[news.topics[i]].numTotalVotes++;
            voters[_voter].ratings[news.topics[i]].numCorrectVotes++;
        }
    }

    function decreaseVoterRating(address _voter) private {
        for (uint i = 0; i < news.topics.length; i++) {
            voters[_voter].ratings[news.topics[i]].numTotalVotes++;
            voters[_voter].ratings[news.topics[i]].numCorrectVotes--;
        }
    }

    function distributeRewards() private {
        uint correctVotes = 0;
        
        for (uint i = 0; i < votes.length; i++) {
            if (votes[i].voteValue == detectedAccuracy) 
                correctVotes++;
        }

        uint rewardAmount = totalDeposit / correctVotes;

        for (uint i = 0; i < votes.length; i++) {
            if (votes[i].voteValue == detectedAccuracy) {
                rewardVoter(votes[i].voter, rewardAmount);
            }
        }
    }

    function rewardVoter(address _voter, uint rewardAmount) private {
        payable(_voter).transfer(rewardAmount);        
    }
    
    function lockVotes() private {
        isLocked = true;
    }

    function unlockNews() public {
        require(msg.sender == news.author, "Not authorized");
        require(isLocked, "News is not locked");
        isLocked = false;
    }
}