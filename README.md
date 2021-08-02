# Ether Cards' Battle Royale Engine
This is the implementation of Ether Cards' Battle Royale Simulator.

The Project Document and the balance data will be linked in this README a bit later.
#TODO add project files

This is one third of the system, the "engine" that plays the games.

The other two parts will be the Web UI and the blockchain accountability layer, which will store enough data to make the games reproducable, so verifiable.

# Instructions
Beeing only a test version you will need a python editor to see the logs of the battle, there is no output file currently.

To create a deck for yourself and the opponent edit the content of the players_info folder. Each player needs to provide an ID and a deck that consits of cards and 
stored in separate json files, where the name of the file should be the id of the card. 
There is currenlty no protection against incorrect ID's so if you give a non existant one the battle simulator will error out. 
Please respect the rules explained in the game design doccumentation or in the video, othervise your deck will be considered invalid and you will get an empy deck.
If you want to add a card to your deck you just need to set the name property to the id of the card found in the excel file, and add it to the array.

At this point you are ready to run the test application.

Once You run it you will see detailed logs on what is the current state of the players, what cards did they play how they performed in each of the 5 phases (neutralizer, boost, combo,defense and attack)

Thank you for helping in testing and making the simulator better!
