module SolverSpec (spec) where

import GameData (start, theCharacters, theMap)
import Solver (allSteps, select, solve, talk, travel, walkthrough)
import Test.Hspec
import TestUtils (testDialogue, testGame)
import Types

-- ghci> walkthrough

spec :: Spec
spec = do
  describe "talk" $ do
    it "matches expected behaviour from ghci example" $ do
      let g = testGame 1

      let results = map snd (talk g testDialogue)
      results
        `shouldBe` [[2, 1], [2, 2], [3]]

  describe "select" $ do
    it "matches expected behaviour from ghci example" $ do
      let g = testGame 1

      let results = select g
      results
        `shouldBe` [ [],
                     ["Russell"],
                     ["Heyting"],
                     ["Heyting", "Russell"],
                     ["Brouwer"],
                     ["Brouwer", "Russell"],
                     ["Brouwer", "Heyting"],
                     ["Brouwer", "Heyting", "Russell"]
                   ]

  describe "travel" $ do
    it "matches expected behaviour from ghci example" $ do
      let m = [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 5)]
      let loc = 0

      let results = travel m loc
      results
        `shouldBe` [ (0, []),
                     (1, [1]),
                     (2, [2]),
                     (3, [2, 3]),
                     (4, [2, 4]),
                     (5, [2, 3, 2])
                   ]

  describe "allSteps" $ do
    it "matches expected behaviour from ghci example" $ do
      let g = Game theMap 1 [] theCharacters
      let results = map fst (allSteps g)

      -- compare using `show` so Eq on Command is not needed
      map show results
        `shouldBe` map
          show
          [ [Travel [], Select ["Luitzen Brouwer"], Talk [3, 1]],
            [Travel [1], Select ["David Hilbert"], Talk [1, 1, 1, 1]],
            [Travel [1], Select ["David Hilbert"], Talk [2]],
            [Travel [1, 2], Select ["Jean-Yves Girard"], Talk []]
          ]

  describe "solve" $ do
    it "matches expected behaviour from ghci example" $ do
      let result = solve start
      map show result
        `shouldBe` map
          show
          [ Travel [],
            Select ["Bertrand Russell"],
            Talk [1, 1],
            Travel [1],
            Select ["Luitzen Brouwer"],
            Talk [3, 1],
            Travel [2],
            Select ["David Hilbert"],
            Talk [1, 1, 1, 1],
            Travel [2],
            Select ["William Howard"],
            Talk [1],
            Travel [1, 3],
            Select ["Jean-Yves Girard"],
            Talk [],
            Travel [1, 1, 3],
            Select ["Haskell Curry", "William Howard"],
            Talk [],
            Travel [2],
            Select ["Bertrand Russell", "Gottlob Frege", "Luitzen Brouwer"],
            Talk [1, 1, 1]
          ]
