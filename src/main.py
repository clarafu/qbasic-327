#!/usr/bin/env python
from qbMod import messages, tx, session, qbUtil
import sys
import getopt
import os
import readline

def printHelpInfo(sessionType):
    if sessionType == session.loggedOutSessionType:
        print "Available Commands: login, quit"
    elif sessionType == session.privilegedSessionType:
        print "Available Commands: logout, quit, createacct, deleteacct, withdraw, deposit, transfer"
    else:
        print "Available Commands: logout, quit, withdraw, deposit, transfer"

def main():

    # control variables
    mainLoop = True
    sessionType = "login"

    # Account list and transaction files
    validAccountsList = []
    transactionList = []

    accountsPendingCreation = []
    accountsPendingDeletion = []
    accountsWithdrawalDict = {}

    validAccoutsListPath = "./validaccounts.txt"
    transactionListPath = "./out"

    # Set up parameters, so we can customize the
    # locations of the inputs/outputs
    try:
        opts, args = getopt.getopt(sys.argv[1:], "v:o:")

        for opt, arg in opts:
            if opt == "-v":
                # Path to the valid accounts file
                validAccoutsListPath = arg
                print messages.getMessage("custValidPath", arg)
            elif opt == "-o":
                # Path to the place we want to store the transaction lists
                transactionListPath = arg
                print messages.getMessage("custTxPath", arg)
    except Exception as e:
        mainLoop = False
        print messages.getMessage("fatalError", str(e))
        return -1

    if not os.path.exists(transactionListPath):
        os.makedirs(transactionListPath)

    if not os.path.exists(validAccoutsListPath):
        # If no valid accounts list exists, create a blank one
        with open(validAccoutsListPath, 'a') as newVaf:
            newVaf.write("0000000\n")
            newVaf.close()

    print messages.getMessage("welcome")

    while mainLoop:
        try:
            inputArgs = raw_input("{}> ".format(sessionType))
            command = inputArgs

            if command == "quit":
                mainLoop = False
            elif command == "login":
                loginSuccess, loginSessionType = session.doLogin(sessionType)

                if loginSuccess:
                    # if the login was successful, we need to read the valid
                    # accounts file and set the session type

                    # Open and process the valid accounts list
                    with open(validAccoutsListPath) as vaf:
                        validAccountsList = vaf.readlines()
                        validAccountsList = [x.strip() for x in validAccountsList]
                        validAccountsList.remove("0000000")

                    sessionType = loginSessionType
                    print messages.getMessage("loggedIn", sessionType)
            elif command == "help":
                printHelpInfo(sessionType)

            elif sessionType == session.loggedOutSessionType and command in ["createacct", "deleteacct", "deposit", "withdraw", "transfer", "logout"]:
                print messages.getMessage("txErrNotLoggedIn")

            elif command == "logout":
                    logoutSuccess = session.doLogout(sessionType)

                    if logoutSuccess:
                        # if the logout was successful, we neet to write a
                        # tx file, clear variables, and set the session type
                        tx.writeTransactionList(transactionList, transactionListPath)

                        del accountsPendingCreation[:]
                        del accountsPendingDeletion[:]
                        del transactionList[:]
                        del validAccountsList[:]
                        accountsWithdrawalDict.clear()

                        print messages.getMessage("loggedOut", sessionType)
                        sessionType = session.loggedOutSessionType

            elif command == "createacct":
                createAccSuccess, transaction, accountNumber = tx.doCreateAcct(sessionType, validAccountsList, accountsPendingCreation, accountsPendingDeletion)

                if createAccSuccess:
                    transactionList.append(transaction)
                    accountsPendingCreation.append(accountNumber)
                    print messages.getMessage("accountCreated", accountNumber)

            elif command == "deleteacct":
                deleteAccSuccess, transaction, accountNumber = tx.doDeleteAcct(sessionType, validAccountsList, accountsPendingCreation, accountsPendingDeletion)

                if deleteAccSuccess:
                    transactionList.append(transaction)
                    accountsPendingDeletion.append(accountNumber)
                    print messages.getMessage("accountDeleted", accountNumber)

            elif command == "deposit":
                depositSuccess, transaction, accountNumber, depositAmount = tx.doDeposit(sessionType, validAccountsList, accountsPendingCreation, accountsPendingDeletion)

                if depositSuccess:
                    transactionList.append(transaction)
                    print messages.getMessage("depositSuccess", [qbUtil.centsToDollars(str(depositAmount)), accountNumber])

            elif command == "transfer":
                transferSuccess, transaction, accountNumber, transferAmount = tx.doTransfer(sessionType, validAccountsList, accountsPendingCreation, accountsPendingDeletion)

                if transferSuccess:
                    transactionList.append(transaction)
                    print messages.getMessage("transferSuccess", [qbUtil.centsToDollars(str(transferAmount)), accountNumber])

            elif command == "withdraw":
                withdrawSuccess, transaction, accountNumber, depositAmount = tx.doWithdraw(sessionType, validAccountsList, accountsPendingCreation, accountsPendingDeletion, accountsWithdrawalDict)

                if withdrawSuccess:
                    transactionList.append(transaction)

                    #add the dollar amount to the dictionary
                    if accountNumber in accountsWithdrawalDict:
                        accountsWithdrawalDict[accountNumber] = accountsWithdrawalDict[accountNumber] + int(depositAmount)
                    else:
                        accountsWithdrawalDict[accountNumber] = int(depositAmount)

                    print messages.getMessage("withdrawSuccess", [qbUtil.centsToDollars(str(depositAmount)), accountNumber])

            else:
                print messages.getMessage("unknownCommand", command)
        except KeyboardInterrupt:
            mainLoop = False
        except EOFError:
            mainLoop = False

    print messages.getMessage("goodbye")


if __name__ == "__main__":
    main()
