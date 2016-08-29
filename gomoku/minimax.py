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
		movesList = []
		spots = board.getOcuppiedSpots(board.nextPlayer)
		moves = []
		for i in range(spots.size()):
			moves.add(board.lookAround(spots.get(i)))

		#move.removeOccupiedones?

		if moves.empty():
			movesList = board.getEmpties()
		else:
			movesList = moves

		if depth == 0:
			return movesList.get(0)
	

# 	/**
# 	 * Minimax algorithm with alpha-beta pruning.
# 	 * @param  depth lookahead
# 	 * @param  myBest alpha
# 	 * @param  theirBest beta
# 	 * @return Object[0] contains (Double) score and Object[1] contains (String) move
# 	 */
# 	Object[] mmab(Board board, int d, double myBest, double theirBest) {
# 		ArrayList<String> moveList;
# 		Set<String> moves = new HashSet<String>();
# 		ArrayList<String> places = board.getPlayerPlaces(board.nextPlayer);
# 		for (int i = 0; i < places.size(); i++) {
# 			moves.addAll(board.lookAround(places.get(i)));
# 		}
# 		moves.retainAll(board.getEmpties());
# 		// make sure that moves is not empty
# 		// otherwise, pick from list of empty locations
# 		if (moves.isEmpty())
# 			moveList = new ArrayList<String>(board.getEmpties());
# 		else
# 			moveList = new ArrayList<String>(moves);

# 		Double bestScore;
# 		Object[] temp;
# 		Double tempScore;
# 		String bestMove = "";

# 		// evaluate at leaf
# 		if (d == 0) {
# 			Object[] x = { evaluate(board), moveList.get(0) };
# 			return x;
# 		}
# 		bestScore = myBest;
# 		while (moveList.size() > 0) {
# 			Board newBoard = new Board(board);
# 			String newMove = moveList.get(0);
# 			newBoard.placeMove(newBoard.nextPlayer, newMove, false);
# 			temp = mmab(newBoard, d - 1, -theirBest, -bestScore);
# 			tempScore = -(Double) temp[0];
# 			if (tempScore > bestScore) {
# 				bestScore = tempScore;
# 				bestMove = newMove;
# 			}
# 			if (bestScore > theirBest) {
# 				Object[] x = { bestScore, bestMove };
# 				return x;
# 			}
# 			moveList.remove(0);
# 		}
# 		Object[] x = { bestScore, bestMove };
# 		return x;
# 	}
# }