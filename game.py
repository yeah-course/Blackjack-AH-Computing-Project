import random
import sqlite3
import bcrypt 
from prettytable import PrettyTable

#function to create database
def createDB():
    conn = sqlite3.connect("UserDetails.db")

    cur = conn.cursor()

    sql_create = '''
        CREATE TABLE IF NOT EXISTS UserDetails (username varchar(25) NOT NULL PRIMARY KEY,
        password varchar NOT NULL,
        chipBalance int NOT NULL);
        '''
    cur.execute(sql_create)
    conn.commit()

#card object
class Card:

    #constructor method for card 
    def __init__(self, suit, rank, value):
        self.__suit = suit
        self.__rank = rank
        self.__value = value

    #printing card method
    def showCard(self):
        lines = [
            "┌─────────┐",
            f"│{self.__rank:<4}     │",     #rank left aligned
            "│         │",
            f"│    {self.__suit}    │",       #centered suit
            "│         │",
            f"│     {self.__rank:>4}│",     #rank right aligned
            "└─────────┘"
        ]
        print("\n".join(lines))

    #value getter method for value
    def getValue(self):
        return self.__value

    #rank getter method
    def getRank(self):
        return self.__rank


#deck object  
class Deck:
    #deck constructor method
    def __init__(self, cards):
        self.__cards = []

    #method to build deck
    def createDeck(self):
        suits = ["♣", "♦", "♥", "♠"]
        #dictionary defining rank to values
        ranksAndValues = {"2":2, "3":3, "4":4,
                          "5":5, "6":6, "7":7,
                          "8":8, "9":9, "10":10,
                          "J":10, "Q":10, "K":10,
                          "A":11}
        #loop through dictionary and assign value to objects for each suit.
        for suit in suits:
            for key, value in ranksAndValues.items():
                cSuit = suit
                cRank = key
                cValue = value
                self.__cards.append(Card(cSuit, cRank, cValue))
        
        return self.__cards

#player object
class Player():
    #player constructor method
    def __init__(self, username, balance):
        self.__username = username
        self.__balance = balance

    #getter methods
    def getUsername(self):
        return self.__username
    
    def getBalance(self):
        return self.__balance
    
#signup function
def signUp():
        username = str(input("Please enter a unique username:\n"))
        #password has to be changed to bytes to hash 
        password = str(input("Please enter a password:\n")).encode('utf-8')

        #generate salt
        salt = bcrypt.gensalt()

        #hash the password
        hashed = bcrypt.hashpw(password, salt)

        #connect to db
        conn = sqlite3.connect("UserDetails.db")
        cur = conn.cursor()

        #check if username already exists
        sql_searchUsers = '''
        SELECT username
        FROM UserDetails
        WHERE username = ?;'''
        
        #execute the query and sub in parameters 
        cur.execute(sql_searchUsers, (username,))
        
        conn.commit()

        #store output of query in output variable
        output = cur.fetchall()

        #if the query returns something, that means a user already has this username
        if len(output) != 0:
            print("That username is already taken.")
            choice = input("Would you like to login (1) or try another username (2)?\n")

            while choice != "1" and choice != "2":
                print("Please pick 1 or 2")
                choice = input("Would you like to login (1) or try another username (2)?\n")

            if choice == "1":
                conn.close()
                return login()

            elif choice == "2":
                conn.close()
                return signUp()

        #add user to database
        sql_addUser = '''
        INSERT INTO UserDetails (username, password, chipBalance)
        VALUES (?, ?, ?);'''
        
        cur.execute(sql_addUser, (username, hashed, 100))

        conn.commit()

        return username    

#login function (for existing user)
def login():
        #get inputs
        username = str(input("Enter your username:\n"))
        password = str(input("Enter your password:\n")).encode('utf-8')

        conn = sqlite3.connect("UserDetails.db")
        cur = conn.cursor()

        #query to get hashed password from database where username matches
        sql_checkDetails = '''
            SELECT username, password
            FROM UserDetails
            WHERE username = ?'''
        
        #sub in variables to query
        cur.execute(sql_checkDetails, (username,))
        conn.commit()

        #store query in variable
        output = cur.fetchall()

        correct = False

        #checks that the user exists, and password right, if not function reruns.
        if len(output) == 0:
            pass

        #using bcrypt.checkpw to return a boolean, true or false, if true passwords match, if false they do not.
        elif bcrypt.checkpw(password, output[0][1]) == True:
            print("Login successful!")
            correct = True
        
        if correct == False:
            print("Incorrect username or password, please try again\n")
            choice = input("Would you like to try logging in again (1) or sign up (2)?\n")

            while choice != "1" and choice != "2":
                print("Please pick 1 or 2")
                choice = input("Would you like to try logging in again (1) or sign up (2)?\n")

            if choice == "1":
                username = login()

            elif choice == "2":
                username = signUp()
        
        return username

#give player option to signup or login
def accountOptions():

    choice = input("Are you a new player? (y/n)\n")

    if choice.lower() == "yes" or choice.lower() == "y":
        username = signUp()

    elif choice.lower() == "no" or choice.lower() == "n":
        username = login()

    else:
        print("please type 'yes'/'y' or 'no'/'n'\n")
        username = accountOptions()
    
    return username

#load all the players in for the leaderboard
def loadPlayers():
    conn = sqlite3.connect("UserDetails.db")
    cur = conn.cursor()
    
    #query to get all usernames and chipBalances from database
    sql_getAllPlayers = '''
        SELECT username, chipBalance
        FROM UserDetails;'''
    
    cur.execute(sql_getAllPlayers)
    result = cur.fetchall()
    conn.close()

    #initialise array of objects for leaderboard
    leaderboard = []

    for username, balance in result:
        leaderboard.append(Player(username, balance))


    #bubble sort to sort players by balance
    temp = 0
    swaps = True
    outer = len(leaderboard) - 1

    while swaps == True and outer >=0:
        
        swaps = False

        for inner in range(0, outer):
            if leaderboard[inner].getBalance() < leaderboard[inner + 1].getBalance():
                temp = leaderboard[inner]
                leaderboard[inner] = leaderboard[inner+1]
                leaderboard[inner + 1] = temp
                
                swaps = True
                
        outer -= 1



    return leaderboard


#game functions 
def validBet(username):

    try:
        bet = float(input("Please enter your bet amount (increments of 10 only)\n"))

    #except for if user enters a string rather than a number, makes sure program doesn't crash and handles the misinput
    except:
        print("Invalid bet amount, please try again.\n")
        bet = validBet(username)
        return bet


    conn = sqlite3.connect("UserDetails.db")
    cur = conn.cursor()

    #query to get player's chip balance
    sql_getBalance = '''
        SELECT chipBalance 
        FROM UserDetails
        WHERE username = ?;'''
    
    cur.execute(sql_getBalance, (username,))
    result = cur.fetchall()
    conn.close()

    balance = result[0][0]

    #check that they have enough chips, and that bet is an increment of 10
    if bet <= balance and bet % 10 == 0 and bet > 0:
        pass

    #if the bet is invalid, ask user again for bet
    elif bet > balance or bet % 10 != 0 or bet <= 0:
        print("You do not have enough chips for this bet!")
        bet = validBet(username)

    return bet

def validBalance(username):
    broke = False

    conn = sqlite3.connect("UserDetails.db")
    cur = conn.cursor()

    #query to get player's chip balance
    sql_getBalance = '''
        SELECT chipBalance 
        FROM UserDetails
        WHERE username = ?;'''
    
    cur.execute(sql_getBalance, (username,))
    result = cur.fetchall()
    conn.close()

    balance = result[0][0]

    if balance == 0:
        print("You have no chips, you are banned from playing. You can either view the leaderboard or leave.")
        
        broke = True
    
    return broke

#betting function
def placeBet(username, bet):

    
    conn = sqlite3.connect("UserDetails.db")
    cur = conn.cursor()

    #query to update player's chip balance after placing bet
    sql_updateBalance = '''
        UPDATE UserDetails
        SET chipBalance = chipBalance - ?
        WHERE username = ?;'''
        
    cur.execute(sql_updateBalance, (bet, username))
    conn.commit()
    conn.close()

    return bet
    



#index for moving through the deck of cards
index = 0

#function for player's initial two cards
def dealInitialCards(deckOfCards, index):

    #keeping an array of cards to use to calculate hand values 
    hand = []  
    bust = False

    #first card
    deckOfCards[index].showCard()
    hand.append(deckOfCards[index])
    
    index += 1

    #second card
    deckOfCards[index].showCard()
    hand.append(deckOfCards[index])
    
    index += 1

    return hand, bust, index

#function for dealer's initial two cards
def DealerCards(deckOfCards, index):

    dealerHand = []
    dealerBust = False
    

    #first card
    deckOfCards[index].showCard()
    dealerHand.append(deckOfCards[index])

    index += 1

    #second card
    deckOfCards[index].showCard()
    dealerHand.append(deckOfCards[index])

    index += 1

    return dealerHand, index, dealerBust


#function to calculate the hand value
def calculateHandValue(hand, bust):
    value = 0
    aces = 0

    #loop through hand
    for card in hand:
        
        value += card.getValue() #total the value of the hand
        if card.getRank() == "A": #count the aces in the hand
            aces += 1

    #handling ace logic 
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    #bust is a boolean of whether the hand value is greater than 21
    bust = value > 21
    return value, bust

def GameOptions(deckOfCards, hand, index, bet, username):
    bust = False

    while True:
        #give the user the double down option on first go
        if len(hand) == 2:
            choice = str(input("Would you like to Hit, Stand, or Double Down? (H/S/DD)\n"))

        #remove double down option on other goes
        else:
            choice = str(input("Would you like to Hit or Stand? (H/S)\n"))

        #hit scenario
        if choice.lower() == "hit" or choice.lower() == "h":

            deckOfCards[index].showCard()
            hand.append(deckOfCards[index])
            index +=1

        #call calculateHandValue to see if player has gone bust
            handValue, bust = calculateHandValue(hand, bust)
            

            if bust:
                return handValue, index, bust, bet
            
        elif choice.lower() == "stand" or choice.lower() == "s":

            handValue, bust = calculateHandValue(hand, bust)
            return handValue, index, bust, bet



        elif (choice.lower() == "double down" or choice.lower() == "dd") and len(hand) == 2:

            valid = False

            #query to check they have enough credits to do this
            conn = sqlite3.connect("UserDetails.db")
            cur = conn.cursor()

            sql_getBalance = '''
                SELECT chipBalance
                FROM UserDetails
                WHERE username = ?;'''

            cur.execute(sql_getBalance, (username,))
            result = cur.fetchall()
            conn.close()

            balance = result[0][0]
            if bet <= balance and bet > 0:
                valid = True

            if bet > balance:
                print("You do not have enough chips to double down, please choose Hit or Stand.\n")

                return GameOptions(deckOfCards, hand, index, bet, username)
            
            if valid == True:
                #query to update their balance in the database
                conn = sqlite3.connect("UserDetails.db")
                cur = conn.cursor()

        
                sql_updateBalance = '''
                    UPDATE UserDetails
                    SET chipBalance = chipBalance - ?
                    WHERE username = ?;'''
        
                cur.execute(sql_updateBalance, (bet, username))
                conn.commit()
                conn.close()

                bet = bet * 2


                deckOfCards[index].showCard()
                hand.append(deckOfCards[index])
                index += 1

            handValue, bust = calculateHandValue(hand, bust)

            if bust:
                return handValue, index, bust, bet

            return handValue, index, bust, bet

        else:
            print("Invalid option. If you picked double down, you can only do this on the first go.\n")


def dealerGameOptions(deckOfCards, dealerHand, index):
    dealerBust = False

    #calculate intial dealer hand value
    dealerHandValue, dealerBust = calculateHandValue(dealerHand, dealerBust)

    while True: 

        if dealerHandValue < 17: 

            print("Dealer hits\n") 
            deckOfCards[index].showCard() 
            dealerHand.append(deckOfCards[index])
            index +=1 
            
            #call calculateHandValue to see if dealer has gone bust 
            dealerHandValue, dealerBust = calculateHandValue(dealerHand, dealerBust) 
            if dealerBust:
                return dealerHandValue, index, dealerBust 
        
        elif dealerHandValue >= 17 and dealerHandValue <= 21: 
            print("Dealer stands")
            dealerBust = False
            return dealerHandValue, index, dealerBust

def updateBalance(username, amount):
    conn = sqlite3.connect("UserDetails.db")
    cur = conn.cursor()

    sql_updateBalance = '''
        UPDATE UserDetails
        SET chipBalance = chipBalance + ?
        WHERE username = ?;'''
    
    cur.execute(sql_updateBalance, (amount, username))
    conn.commit()
    conn.close()


def compareHands(handValue, dealerHandValue, bust, dealerBust, username, bet, hand, dealerHand):
    #player winning cases
    #blackjack case
    if handValue == 21 and dealerHandValue != 21 and len(hand) == 2:
        #3 for 2
        winnings = int(bet * 2.5)

        print("Blackjack! You win", winnings)

        updateBalance(username, winnings)
    #dealer goes bust
    elif bust == False and dealerBust == True:
        
        winnings = bet*2

        print("Dealer has gone bust, you win", winnings)

        updateBalance(username, winnings)
    #better hand
    elif handValue > dealerHandValue and bust == False:
        
        #update player's chip balance
        winnings = bet*2

        print("You have beat the dealer! You win", winnings)

        updateBalance(username, winnings)

    #dealer winning cases
    #dealer gets blackjack
    elif dealerHandValue == 21 and handValue !=21 and len(dealerHand) == 2:
        print("Dealer has blackjack, dealer wins! You lost", bet)

    #player goes bust
    elif bust == True and dealerBust == False:
        print("You have gone bust, dealer wins! You lost", bet)

    #better hand
    elif dealerHandValue > handValue and dealerBust == False:
        print("Dealer has beaten you, dealer wins! You lost", bet)

    #both go bust
    elif bust == True and dealerBust == True:
        print("Both you and the dealer have gone bust, dealer wins! You lost", bet)

    #push cases

    #both player and dealer get blackjack
    elif handValue == 21 and dealerHandValue == 21 and len(hand) == 2 and len(dealerHand) == 2:
        print("Both you and the dealer have blackjack, it's a push!")

        winnings = bet

        updateBalance(username, winnings)
    
    #equal hand values
    elif handValue == dealerHandValue and bust == False:
        print("It's a push!")

        winnings = bet

        updateBalance(username, winnings)

def showCurrentBalance(username):
    conn = sqlite3.connect("UserDetails.db")
    cur = conn.cursor()

    sql_getBalance = '''
        SELECT chipBalance
        FROM UserDetails
        WHERE username = ?;'''

    cur.execute(sql_getBalance, (username,))
    balance = cur.fetchone()
    

    conn.commit()
    conn.close()
    
    chips = balance[0]
    print("Your current chip balance is:", chips)


def firstChoice():
    choice = str(input("Would you like to play the game (1), view the leaderboard (2), or leave (3)?\n"))

    if choice != "1" and choice != "2" and choice != "3":
        print("Please pick 1, 2, or 3")
        choice = firstChoice()
    
    return choice



def playAgain(game):
    play = str(input("Would you like to play again? (y/n)\n"))

    if play.lower() == "yes" or play.lower() == "y":
        pass

    elif play.lower() == "no" or play.lower() == "n":
        game = False

    elif play.lower() != "yes" and play.lower() != "no" and play.lower() != "y" and play.lower() != "n":
        print("Please pick yes or no.")
        game = playAgain(game)

    return game



#main code

#login stuff
createDB()

username = accountOptions()

showCurrentBalance(username)






#game stuff
#initialise array of objects (card objects)
cards = Deck([])

#create deck of cards and shuffe them
deckOfCards = cards.createDeck()
random.shuffle(deckOfCards)

outer = True

while outer:


    choice = firstChoice()

    if choice == "1":
        #start game loop
        game = True
        while game:

            broke = validBalance(username)

            if broke == True:
                break

            bet = validBet(username)

            bet = placeBet(username, bet)

            print("Here are the dealer's initial two cards:\n")
            dealerHand, index, dealerBust = DealerCards(deckOfCards, index)


            print("Here are your initial two cards:\n")
            hand, bust, index = dealInitialCards(deckOfCards, index)



            handValue, index, bust, bet = GameOptions(deckOfCards, hand, index, bet, username)

            dealerHandValue, index, dealerBust = dealerGameOptions(deckOfCards, dealerHand, index)

            compareHands(handValue, dealerHandValue, bust, dealerBust, username, bet, hand, dealerHand)

            showCurrentBalance(username)

            #if approaching end of the deck reshuffle 
            if index >= 45:
                random.shuffle(deckOfCards)
                index = 0

            
            game = playAgain(game)



    elif choice == "2":
        leaderboard = loadPlayers()
        print("Leaderboard:")

        #create columns for leaderboard table
        t = PrettyTable(['Rank', 'Username', 'Chip Balance'])

        #add each object from leaderbord
        for i in range(len(leaderboard)):
            t.add_row([i+1, leaderboard[i].getUsername(), leaderboard[i].getBalance()])

        print(t)

    
    elif choice == "3":
        print("Thanks for playing!")
        break 
        