module Types where

type Character = String

type Party = [Character]

type Node = Int

type Location = String

type Map = [(Node, Node)]

data Game
  = Over
  | Game Map Node Party [Party]
  deriving (Eq, Show)

type Event = Game -> Game

data Dialogue
  = Action String Event
  | Branch (Game -> Bool) Dialogue Dialogue
  | Choice String [(String, Dialogue)]

data Command = Travel [Int] | Select Party | Talk [Int]
  deriving (Show)

type Solution = [Command]
