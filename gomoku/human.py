#player.py
import player

class Human:

	def _init__(self, side, first):
		Player.__init__(side, first)

	def takeTurn():
		move = pickMove()
		board.placeMove(me, move)
		print(board)
		return move
	

	def move():
		move = ram_input("What's your move?(enter coordinates)")
		if move in board.emptySpots():
			return move
		return -100
