# Set
Mathematics of the Set card game

Set is a matching card game, but not like the simple memory match game.
(See the adjacent_pairs repository for that.)

Each card in a Set deck has 1,2, or 3 shapes on it.
The shapes are diamonds, ovals, or squiggles; they are red, green, or purple; and they are empty, striped, or solid.

Each possible card is in the deck for a total of 3^4 = 81 cards.

Within the game, a three-card triple is a SET if and only if the cards are all the same or all different for each property.

This code calculates how many sets there are at the beginning of the game, when 12 randomly selected cards are laid out together.
It generates a histogram, and evaluates the code execution time for different set-counting methods.
