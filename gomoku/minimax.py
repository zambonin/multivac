#minmax class

class Minimax:
	# here we will evaluate with the heuristic.

	def evaluate(self, board):
		oneTuple = board.possibleWins(board.lastPlayer, 1)
		twoTuple = board.possibleWins(board.lastPlayer, 2)
		threeTuple = board.possibleWins(board.lastPlayer, 3)
		heuristic = oneTuple + twoTuple + threeTuple
		return heuristic

	def minimax(self, board, depth, alpha, beta):
		movesList = defaultdict(dict)
		spots = board.getOcuppiedSpots(board.nextPlayer)
		moves = defaultdict(dict)
		for i in range(spots.size()):
			moves.add(board.lookAround(spots.get(i)))

		#move.removeOccupiedones?

		if moves.empty():
			movesList = board.getEmpties()
		else:
			movesList = moves

		if depth == 0:
			return movesList.get(0)
	
