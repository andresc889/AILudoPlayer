# AI Ludo Player

I worked on this project with my teammate Deepak Aravindakshan. This was our final project for our Artificial Intelligence class. The goal was to replicate the results of earlier work in reinforcement learning. Ludo is a stochastic race board game in which players can attack each other. We implemented Q-learning with a neural network to allow an agent to learn a game strategy.

We could not fully replicate previous results. It turns out that Q-learning is hard to tune (even more so when neural networks are used). I have experimented a little more with the code and the agent tends to become dumber as it trains more. I have not been able to figure out the reason, but I am making the source code available nonetheless.

Please visit https://www.cs.colostate.edu/~andrescj/proj/ai_ludo_player/ for details.

The src folder contains the source code in Python. You can think of ql_trainer.py as the "entry point." To use the neural network, it is necessary to download FANN and the corresponding Python bindings (http://leenissen.dk/).

The ludo_board.gif file in the src folder is a modification of an image found in Wikipedia:

https://commons.wikimedia.org/wiki/File:Ludo_board.svg
