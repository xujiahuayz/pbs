//
// Created by Aaryan Gulia on 19/01/2024.
//

#ifndef PBS_C_AUCTION_H
#define PBS_C_AUCTION_H
#include "vector"
#include "blockchain_env/Builder.h"
#include "factory/BuilderFactory.h"

class Auction {

public:
    BuilderFactory &builderFactory;
    std::shared_ptr<Block> auctionBlock;
    TransactionFactory &transactionFactory;
    double auctionTime = 0;

    Auction(BuilderFactory &mBuilderFactory,TransactionFactory &mTransactionFactory);

    void runAuction();
};


#endif //PBS_C_AUCTION_H
