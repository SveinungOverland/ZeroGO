# Monte carlo tree search

### What is Monte carlo

This algorithm is used to find the best route to a reward without hogging the memory. It learns from itself and does not use domain-knowlege and chooses the most promising path. The search tree weights all possible actions based on a given policy, that policy is telling to expolore or exploit a given branch.  It's using rollout methods such illustraded under.  

The most basic way to use playouts is to apply the same number of playouts after each legal move of the current player, then choose the move which led to the most victories. The efficiency of this method—called Pure Monte Carlo Game Search—often increases with time as more playouts are assigned to the moves that have frequently resulted in the current player's victory according to previous playouts. Each round of Monte Carlo tree search consists of four steps:
	
 * Selection: start from root R and select successive child nodes until a leaf node L is reached. The root is the current game state and a leaf is any node from which no simulation (playout) has yet been initiated. The section below says more about a way of biasing choice of child nodes that lets the game tree expand towards the most promising moves, which is the essence of Monte Carlo tree search.
 * Expansion: unless L ends the game decisively (e.g. win/loss/draw) for either player, create one (or more) child nodes and choose node C from one of them. Child nodes are any valid moves from the game position defined by L.
 * Simulation: complete one random playout from node C. This step is sometimes also called playout or rollout. A playout may be as simple as choosing uniform random moves until the game is decided (for example in chess, the game is won, lost, or drawn).
Backpropagation: use the result of the playout to update information in the nodes on the path from C to R.

[![Steps of MCTS](https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/MCTS_%28English%29_-_Updated_2017-11-19.svg/2880px-MCTS_%28English%29_-_Updated_2017-11-19.svg.png)](https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/MCTS_%28English%29_-_Updated_2017-11-19.svg/2880px-MCTS_%28English%29_-_Updated_2017-11-19.svg.png)

### Usage of MC

The tree search is used to find the best path for the Go player. It's used to train our NN to give the best actions to take in a given state. 

