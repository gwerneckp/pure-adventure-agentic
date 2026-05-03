module GameWorldSpec (spec) where

import GameWorld
import Test.Hspec
import TestUtils (testGame)
import Types

spec :: Spec
spec = do
  describe "connected" $ do
    it "handles example from coursework description" $ do
      connected [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4)] 2 `shouldBe` [0, 1, 3, 4]

    it "returns empty list for empty map" $
      connected [] 0 `shouldBe` []

    it "returns empty list when node has no connections" $
      connected [(1, 2), (3, 4)] 0 `shouldBe` []

    it "returns connected nodes for a given node" $
      connected [(0, 1), (0, 2), (1, 2)] 0 `shouldBe` [1, 2]

  describe "connect" $ do
    it "handles example from coursework description" $ do
      connect 4 0 [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4)] `shouldBe` [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)]

    it "adds a connection to empty map" $
      connect 0 1 [] `shouldBe` [(0, 1)]

    it "adds a connection to existing map" $
      connect 2 3 [(0, 1)] `shouldBe` [(0, 1), (2, 3)]

    it "doesn't add duplicate connections" $ do
      connect 0 1 [(0, 1)] `shouldBe` [(0, 1)]

    it "doesn't add duplicate connections in reverse order" $ do
      connect 1 0 [(0, 1)] `shouldBe` [(0, 1)]

    it "doesn't add self-connections" $ do
      connect 0 0 [(1, 2)] `shouldBe` [(1, 2)]

    it "insert in the middle" $
      connect 1 3 [(0, 1), (1, 2), (2, 4)]
        `shouldBe` [(0, 1), (1, 2), (1, 3), (2, 4)]

    it "insert at front" $
      connect 0 5 [(1, 2), (2, 3)]
        `shouldBe` [(0, 5), (1, 2), (2, 3)]

    it "insert at end" $
      connect 7 8 [(1, 2), (3, 4)]
        `shouldBe` [(1, 2), (3, 4), (7, 8)]

    it "reverse ordering input" $
      connect 5 2 [(1, 2), (2, 3), (3, 9)]
        `shouldBe` [(1, 2), (2, 3), (2, 5), (3, 9)]

    it "rejects self loops" $
      connect 3 3 [(1, 2), (2, 3)]
        `shouldBe` [(1, 2), (2, 3)]

    it "rejects duplicates" $
      connect 2 3 [(1, 2), (2, 3), (3, 4)]
        `shouldBe` [(1, 2), (2, 3), (3, 4)]

  describe "disconnect" $ do
    it "handles example from coursework description" $ do
      disconnect 2 0 [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)]
        `shouldBe` [(0, 1), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)]

    it "removes a connection from map" $
      disconnect 0 1 [(0, 1), (1, 2)] `shouldBe` [(1, 2)]

    it "doesn't affect map if connection doesn't exist" $
      disconnect 0 1 [(2, 3)] `shouldBe` [(2, 3)]

    it "handles empty map" $
      disconnect 0 1 [] `shouldBe` []

    it "removes connection regardless of order" $
      disconnect 1 0 [(0, 1), (1, 2)] `shouldBe` [(1, 2)]

    it "handles removing last connection" $
      disconnect 2 3 [(2, 3)] `shouldBe` []

  describe "add" $ do
    it "handles example from coursework description" $
      add ["Dijkstra"] (testGame 0)
        `shouldBe` Game
          [(0, 1)]
          0
          ["Dijkstra", "Russell"]
          [[], ["Brouwer", "Heyting"]]

    it "keeps ordering when new character should go first" $
      add ["Armando"] (testGame 0)
        `shouldBe` Game
          [(0, 1)]
          0
          ["Armando", "Russell"]
          [[], ["Brouwer", "Heyting"]]

    it "keeps ordering when new character should go last" $
      add ["Zara"] (testGame 0)
        `shouldBe` Game
          [(0, 1)]
          0
          ["Russell", "Zara"]
          [[], ["Brouwer", "Heyting"]]

    it "removes duplicates" $
      add ["Russell"] (testGame 0)
        `shouldBe` testGame 0

    it "does nothing when game is Over" $
      add ["Pia"] Over `shouldBe` Over

  describe "addAt" $ do
    -- no example given in coursework description

    it "adds to empty party at a location" $
      addAt 0 ["A"] (Game [] 0 [] [[], ["X"]])
        `shouldBe` Game [] 0 [] [["A"], ["X"]]

    it "keeps ordering" $
      addAt 0 ["B"] (Game [] 0 [] [["A", "C"], []])
        `shouldBe` Game [] 0 [] [["A", "B", "C"], []]

    it "removes duplicates" $
      addAt 1 ["Y"] (Game [] 0 [] [["X"], ["Y", "Z"]])
        `shouldBe` Game [] 0 [] [["X"], ["Y", "Z"]]

    it "keeps ordering and removes duplicates in same operation" $
      addAt 1 ["A", "Y", "C"] (Game [] 0 [] [["X"], ["A", "B", "Z"]])
        `shouldBe` Game [] 0 [] [["X"], ["A", "B", "C", "Y", "Z"]]

    it "does nothing on Over" $
      addAt 0 ["X"] Over `shouldBe` Over

    it "does nothing for negative index" $
      addAt (-1) ["X"] (testGame 0)
        `shouldBe` testGame 0

    it "does nothing when index too large" $
      addAt 10 ["X"] (testGame 0)
        `shouldBe` testGame 0

    it "does not mutate other parties" $
      addAt 0 ["A"] (Game [] 0 [] [["Z"], ["B"]])
        `shouldBe` Game [] 0 [] [["A", "Z"], ["B"]]

  describe "addHere" $ do
    it "handles example from coursework description" $
      addHere ["Heyting", "Russell"] (Game [(0, 1)] 0 ["Dijkstra"] [[], ["Brouwer"]])
        `shouldBe` Game [(0, 1)] 0 ["Dijkstra"] [["Heyting", "Russell"], ["Brouwer"]]

    it "adds to a non-empty location party" $
      addHere
        ["A"]
        (Game [] 1 [] [["X"], ["B"]])
        `shouldBe` Game [] 1 [] [["X"], ["A", "B"]]

    it "preserves ordering and removes duplicates" $
      addHere
        ["B", "A", "A"]
        (Game [] 0 [] [["A", "C"]])
        `shouldBe` Game [] 0 [] [["A", "B", "C"]]

    it "does nothing when adding empty list" $
      addHere
        []
        (Game [] 0 [] [["X"]])
        `shouldBe` Game [] 0 [] [["X"]]

    it "does nothing on Over" $
      addHere ["X"] Over `shouldBe` Over

  describe "remove" $ do
    it "handles example from coursework description" $
      remove ["Brouwer", "Russell"] (Game [(0, 1)] 0 ["Dijkstra", "Russell"] [[], ["Brouwer", "Heyting"]])
        `shouldBe` Game
          [(0, 1)]
          0
          ["Dijkstra"]
          [[], ["Brouwer", "Heyting"]]

    it "does nothing when given an empty remove list" $
      remove [] (Game [] 0 ["A", "B"] [["X"]])
        `shouldBe` Game [] 0 ["A", "B"] [["X"]]

    it "ignores names not present in the party" $
      remove ["Z"] (Game [] 0 ["A", "B"] [["X", "Y"]])
        `shouldBe` Game [] 0 ["A", "B"] [["X", "Y"]]

    it "removes multiple matching names from the party" $
      remove
        ["A", "C"]
        (Game [] 0 ["A", "B", "C", "D"] [])
        `shouldBe` Game [] 0 ["B", "D"] []

    it "handles duplicate names in the remove list" $
      remove
        ["A", "A", "B"]
        (Game [] 0 ["A", "B", "C"] [])
        `shouldBe` Game [] 0 ["C"] []

    it "does not modify NPC lists" $
      remove
        ["X", "A"]
        (Game [] 0 ["A", "B"] [["X", "Y"], ["A", "Z"]])
        `shouldBe` Game [] 0 ["B"] [["X", "Y"], ["A", "Z"]]

    it "leaves event unchanged when party is empty" $
      remove
        ["A", "B"]
        (Game [] 0 [] [["A"]])
        `shouldBe` Game [] 0 [] [["A"]]

    it "returns Over when removing from Over" $
      remove ["A", "B"] Over
        `shouldBe` Over

  describe "removeAt" $ do
    it "handles example from coursework description" $
      removeAt 1 ["Heyting"] (Game [(0, 1)] 0 ["Dijkstra"] [[], ["Brouwer", "Heyting"]])
        `shouldBe` Game
          [(0, 1)]
          0
          ["Dijkstra"]
          [[], ["Brouwer"]]

    it "removes multiple names when present" $
      removeAt
        0
        ["A", "C"]
        (Game [] 0 [] [["A", "B", "C", "D"]])
        `shouldBe` Game [] 0 [] [["B", "D"]]

    it "ignores names not in the target party" $
      removeAt
        0
        ["Z"]
        (Game [] 0 [] [["A", "B"]])
        `shouldBe` Game [] 0 [] [["A", "B"]]

    it "handles empty remove list" $
      removeAt
        0
        []
        (Game [] 0 [] [["X", "Y"]])
        `shouldBe` Game [] 0 [] [["X", "Y"]]

    it "does not affect other locations" $
      removeAt
        1
        ["A"]
        (Game [] 1 [] [["X"], ["A", "B", "C"]])
        `shouldBe` Game [] 1 [] [["X"], ["B", "C"]]

    it "does nothing when target location is empty" $
      removeAt
        0
        ["A"]
        (Game [] 0 [] [[]])
        `shouldBe` Game [] 0 [] [[]]

    it "does nothing on negative index" $
      removeAt
        (-1)
        ["A"]
        (Game [] 0 [] [["A"]])
        `shouldBe` Game [] 0 [] [["A"]]

    it "does nothing when index too large" $
      removeAt
        10
        ["A"]
        (Game [] 0 [] [["A"]])
        `shouldBe` Game [] 0 [] [["A"]]

    it "returns Over unchanged" $
      removeAt 0 ["A"] Over
        `shouldBe` Over

  describe "removeHere" $ do
    -- no example given in coursework description
    it "removes multiple names at current location" $
      removeHere
        ["A", "C"]
        (Game [] 1 [] [["X"], ["A", "B", "C", "D"]])
        `shouldBe` Game [] 1 [] [["X"], ["B", "D"]]

    it "ignores missing names" $
      removeHere
        ["Z"]
        (Game [] 0 [] [["A", "B"]])
        `shouldBe` Game [] 0 [] [["A", "B"]]

    it "removes nothing when given empty list" $
      removeHere
        []
        (Game [] 0 [] [["A"]])
        `shouldBe` Game [] 0 [] [["A"]]

    it "does not affect other locations" $
      removeHere
        ["A"]
        (Game [] 1 [] [["A"], ["A", "B"]])
        `shouldBe` Game [] 1 [] [["A"], ["B"]]

    it "handles empty party at location" $
      removeHere
        ["A"]
        (Game [] 0 [] [[]])
        `shouldBe` Game [] 0 [] [[]]

    it "returns Over unchanged" $
      removeHere ["A"] Over `shouldBe` Over
