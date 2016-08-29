#computerPlayer.py
from numpy import inf
import player

class Computer:

	def _init__(self, side, first):
		Player.__init__(side, first)

	def takeTurn(self):
		move = pickMove();
		board.placeMove(me, move)
		print(board)
		return move

	def pickMove(self):
		move = Minimax.minimax(board, 1, inf, -inf)
		return move

	def firstMove():
		move = "7 7"
		board.placeMove(me, move)
		print(board)
		return move
