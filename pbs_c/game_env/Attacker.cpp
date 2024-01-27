//
// Created by Aaryan Gulia on 26/01/2024.
//

#include "Attacker.h"
#include "factory/BuilderFactory.h"

Attacker::Attacker(TransactionFactory& transactionFactory,  BuilderFactory& builderFactory)
        : transactionFactory(transactionFactory), builderFactory(builderFactory) {}

void Attacker::attack(int idHint) {
    int counter = 0;
    for (auto& transaction : transactionFactory.transactions) {
        if (transaction.mev > (transaction.gas) * 2 && find_if(targetTransactions.begin(), targetTransactions.end(),
                                                               [&](std::shared_ptr<Transaction>& t){return t->id == transaction.id;}) == targetTransactions.end()) {
            targetTransactions.push_back(std::make_shared<Transaction>(transaction));
            frontTransactions.push_back(std::make_shared<Transaction>(Transaction(transaction.gas + 0.01, 0, attackCounter)));
            backTransactions.push_back(std::make_shared<Transaction>(Transaction(transaction.gas - 0.01, 0, attackCounter++ * -1)));
            counter++;
        }
    }

    for(int i = 0; i < counter; i++) {
        std::cout<<"Attacker's transactions ID: "<<frontTransactions[frontTransactions.size() - 1 - i]->id<<std::endl;
        std::cout<<"Attacker's transactions ID: "<<backTransactions[frontTransactions.size() - 1 - i]->id<<std::endl;
        transactionFactory.createTransactions(*frontTransactions[frontTransactions.size() - 1 - i]);
        transactionFactory.createTransactions(*backTransactions[backTransactions.size() - 1 - i]);
    }
}
void Attacker::results(std::vector<std::shared_ptr<Block>> blocks) {
    double profit = 0.0;
    for (auto& block : blocks) {
        for (int i = 0; i < block->transactions.size(); i++) {
            auto& transaction = block->transactions[i];

            // Check if the transaction is one of the attacker's transactions
            if (std::find(frontTransactions.begin(), frontTransactions.end(), transaction) != frontTransactions.end() ||
                std::find(backTransactions.begin(), backTransactions.end(), transaction) != backTransactions.end()) {
                profit -= transaction->gas;
            }

            // Check if the transaction is a successful attack
            if (std::find(targetTransactions.begin(), targetTransactions.end(), transaction) != targetTransactions.end() &&
                i > 0 && std::find(frontTransactions.begin(), frontTransactions.end(), block->transactions[i - 1]) != frontTransactions.end() &&
                i < block->transactions.size() - 1 && std::find(backTransactions.begin(), backTransactions.end(), block->transactions[i + 1]) != backTransactions.end()) {
                profit += transaction->mev;
            }
        }
    }

    std::cout << "Attacker's profit: " << profit << std::endl;
}

void Attacker::removeFailedAttack(std::shared_ptr<Block> block) {
    int counter = 0;
    for (auto& targetTransaction : targetTransactions) {
        if(targetTransaction == nullptr){
            continue;
        }
        auto trans = std::find_if(block->transactions.begin(), block->transactions.end(),
                     [&](std::shared_ptr<Transaction> t){return t->id == targetTransaction->id;});
        // Check if the target transaction is not in the transaction factory
        if (trans != block->transactions.end()) {
            builderFactory.clearMempools(frontTransactions[counter]);
            transactionFactory.deleteTransaction(frontTransactions[counter]);
            builderFactory.clearMempools(backTransactions[counter]);
            transactionFactory.deleteTransaction(backTransactions[counter]);
            frontTransactions.erase(frontTransactions.begin() + counter);
            backTransactions.erase(backTransactions.begin() + counter);
            targetTransactions.erase(targetTransactions.begin() + counter);
        }
        counter++;
    }
}
