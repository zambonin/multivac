#player.py

class Player:

	def _init__(self, first):
		self.board = GomokuBoard()
		self.me = 1 if first else -1
		self.other = -1 if first else 1
		self.first = first

	#get opponent's play and update board
	def recieveTurn(move):
		board.placeMove(other, move, true)
		return move
	


