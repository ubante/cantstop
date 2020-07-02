# cant stop
I found this simple game at https://boardgamearena.com/gamepanel?game=cantstop and 
the rules are at https://en.wikipedia.org/wiki/Can%27t_Stop_(board_game)#Rules

There were a couple of questions I had about decision making.  This repo will 
simulate the game to answer these questions.

So far, I've learned to choose 7.  For more critical analysis, check out
https://www.aaai.org/ocs/index.php/FLAIRS/2009/paper/download/123/338 

## glossary
* pair-sum: sum of two dice
* attempt: the roll of four dice
* turn: the chance to make attempts to advance your markers and make temp progress
* temp progress: until the player stops, all marker progress is temporary and can be lost 
if the next attempt does not hit
* marker: the temp progress on a single column
* free marker: a marker that can be placed on an available column
* available column: a column where a player has not placed a marker in the top rank
* tournament: a series of games
* round: a set of turns where each player gets exactly one turn
* game: a set of rounds until a player wins three columns
* column combinations: set of up to three columns the player will make in each turn
