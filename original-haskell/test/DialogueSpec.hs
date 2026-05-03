module DialogueSpec (spec, line0) where

import Data.Foldable (find)
import Dialogue
import Dialogue (DialogueInput (..), DialogueStep (DeadEnd), dialoguePure)
import GameWorld
import Test.Hspec
import Test.Hspec (expectationFailure)
import TestUtils (testDialogue, testGame)
import Types
import Types (Game (Over))

spec :: Spec
spec = do
  describe "dialogue coursework.pdf example" $ do
    it "node 0 does not change the game" $ do
      let g = testGame 0

      case dialoguePure g testDialogue DialogueNoInput of
        DeadEnd msg -> do
          msg `shouldBe` "Russell: Let's get our team together and head to Error."
        _ -> expectationFailure "Expected DeadEnd"

    it "node 1 presents choices, when choosing 3, adds Brouwer to the team" $ do
      let g = testGame 1

      case dialoguePure g testDialogue DialogueNoInput of
        NeedChoice isInvalid (Choice msg opts) -> do
          msg `shouldBe` "Brouwer: How can I help you?"
          length opts `shouldBe` 3

          case dialoguePure g (Choice msg opts) (DialogueValidInput 3) of
            DoAction msg' ev -> do
              msg' `shouldBe` "Brouwer: Of course."
              let (Game _ _ party npcs) = ev g
              party `shouldBe` ["Brouwer", "Russell"]
              npcs !! 1 `shouldBe` ["Heyting"]
            _ -> expectationFailure "Expected DoAction after choosing option 3"
        _ -> expectationFailure "Expected NeedChoice"

  describe "findDiaogue coursework.pdf example" $ do
    it "returns line0 when empty party" $ do
      case dialoguePure Over (findDialogue []) DialogueNoInput of
        DoAction msg ev -> do
          msg `shouldBe` line0
          ev Over `shouldBe` Over
        _ -> expectationFailure "Expected DoAction for empty party"

    it "returns Haskell Curry and William Howard dialogue" $ do
      -- side note: we are passing Over here to test the dialogue,
      -- the dialogue conditional branch looks like this Branch (not . isconn 6 7) (Action "..." a_transformation_on_game) (end "...")
      -- because we are passing Over, the condition not . is conn 6 7 will evaluate to not False == True, so the first branch will be taken
      -- the transformations on game will act as id as all the Event(s) we defined have Over -> Over case
      -- therefore the transformations will act as id, which is what the coursework.pdf example expects

      case dialoguePure Over (findDialogue ["Haskell Curry", "William Howard"]) DialogueNoInput of
        DoAction msg ev -> do
          msg `shouldStartWith` "Curry:  You know the way to Error, right?" -- dialogue is
          ev Over `shouldBe` Over
        _ -> expectationFailure "Expected DoAction for Haskell Curry and William Howard dialogue"

    it "handles invalid and exit inputs as expected" $ do
      -- out of bounds inputs
      let NeedChoice _ dlg'@(Choice msg opts) = dialoguePure Over testDialogue DialogueNoInput
      msg `shouldBe` "Brouwer: How can I help you?"

      let NeedChoice isInvalid _ = dialoguePure Over dlg' (DialogueValidInput 4)
      isInvalid `shouldBe` True

      -- coursework.pdf uses "Q" for this test, but because of the separation of concerns of parsing and dialogue handling, parsing input is done in IO layer, we represent invalid inputs internally as DialogueInvalidInput
      let NeedChoice isInvalid _ = dialoguePure Over dlg' (DialogueInvalidInput)
      isInvalid `shouldBe` True

      -- exit input
      -- doing assertion with case as Exit has no fields
      case dialoguePure Over dlg' (DialogueValidInput 0) of
        Exit -> return ()
        _ -> expectationFailure "Expected Exit on choice 0"
