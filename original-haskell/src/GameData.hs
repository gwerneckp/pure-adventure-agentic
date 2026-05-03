module GameData where

import GameWorld
import Types

start :: Game
start = Game theMap 0 [] theCharacters

theMap :: Map
theMap = [(1, 2), (1, 6), (2, 4)]

theLocations :: [Location]
theLocations =
  [ "Home", -- 0
    "Brewpub", -- 1
    "Hotel", -- 2
    "Hotel room n+1", -- 3
    "Temple", -- 4
    "Back of temple", -- 5
    "Takeaway", -- 6
    "The I-50" -- 7
  ]

theDescriptions :: [String]
theDescriptions =
  [ "your own home. It is very cosy.",
    "the `Non Tertium Non Datur' Brewpub & Barber's.",
    "the famous Logicester Hilbert Hotel & Resort.",
    "front of Room n+1 in the Hilbert Hotel & Resort. You knock.",
    "the Temple of Linearity, Logicester's most famous landmark, designed by Le Computier.",
    "the back yard of the temple. You see nothing but a giant pile of waste paper.",
    "Curry's Indian Takeaway, on the outskirts of Logicester.",
    "a car on the I-50 between Logicester and Computerborough. The road is blocked by a large, threatening mob."
  ]

theCharacters :: [Party]
theCharacters =
  [ ["Bertrand Russell"], -- 0  Home
    ["Arend Heyting", "Luitzen Brouwer"], -- 1  Brewpub
    ["David Hilbert"], -- 2  Hotel
    ["William Howard"], -- 3  Hotel room n+1
    ["Jean-Yves Girard"], -- 4  Temple
    [], -- 5  Back of temple
    ["Haskell Curry", "Jean-Louis Krivine"], -- 6  Curry's takeaway
    ["Gottlob Frege"] -- 7  I-50
  ]

theDialogues :: [(Party, Dialogue)]
theDialogues =
  let always _ = True
      end str = Choice str []

      isconn _ _ Over = False
      isconn i j (Game m _ _ _) = elem i (connected m j)

      here Over = 0
      here (Game _ n _ _) = n

      inParty _ Over = False
      inParty c (Game _ _ p _) = elem c p

      isAt _ _ Over = False
      isAt n c (Game _ _ _ ps) = elem c (ps !! n)

      updateMap _ Over = Over
      updateMap f (Game m n p ps) = Game (f m) n p ps
   in [ ( ["Russell"],
          Choice
            "Russell: Let's go on an adventure!"
            [ ("Sure.", end "You pack your bags and go with Russell."),
              ("Maybe later.", end "Russell looks disappointed.")
            ]
        ),
        (["Heyting", "Russell"], end "Heyting: Hi Russell, what are you drinking?\nRussell: The strong stuff, as usual."),
        ( ["Bertrand Russell"],
          Branch
            (isAt 0 "Bertrand Russell")
            ( let intro = "A tall, slender, robed character approaches your home. When he gets closer, you recognise him as Bertrand Russell, an old friend you haven't seen in ages. You invite him in.\n\nRussell: I am here with an important message. The future of Excluded-Middle Earth hangs in the balance. The dark forces of the Imperator are stirring, and this time, they might not be contained.\n\nDo you recall the artefact you recovered in your quest in the forsaken land of Error? The Loop, the One Loop, the Loop of Power? It must be destroyed. I need you to bring together a team of our finest Logicians, to travel deep into Error and cast the Loop into lake Bottom. It is the only way to terminate it."
                  re1 = ("What is the power of the Loop?", Choice "Russell: for you, if you put it on, you become referentially transparent. For the Imperator, there is no end to its power. If he gets it in his possession, he will vanquish us all." [re2])
                  re2 = ("Let's go!", Action "Let's put our team together and head for Error." (updateMap (connect 1 0) . add ["Bertrand Russell"] . removeHere ["Bertrand Russell"]))
               in Choice intro [re1, re2]
            )
            ( Branch
                ((== 7) . here)
                (end "Russell: Let me speak to him and Brouwer.")
                (end "Russell: We should put our team together and head for Error.")
            )
        ),
        ( ["Arend Heyting"],
          Choice
            "Heyting: What can I get you?"
            [ ("A pint of Ex Falso Quodbibet, please.", end "There you go."),
              ("The Hop Erat Demonstrandum, please.", end "Excellent choice."),
              ("Could I get a Maltus Ponens?", end "Mind, that's a strong one.")
            ]
        ),
        ( ["Luitzen Brouwer"],
          Branch
            (isAt 1 "Luitzen Brouwer")
            ( Choice
                "Brouwer: Haircut?"
                [ ( "Please.",
                    let intro = "Brouwer is done and holds up the mirror. You notice that one hair is standing up straight."
                        r1 i = ("There's just this one hair sticking up. Could you comb it flat, please?", d i)
                        r2 = ("Thanks, it looks great.", end "Brouwer: You're welcome.")
                        d i
                          | i == 0 = Choice intro [r2]
                          | otherwise = Choice intro [r1 (i - 1), r2]
                     in d 100
                  ),
                  ("Actually, could you do a close shave?", end "Of course. I shave everyone who doesn't shave themselves."),
                  ( "I'm really looking for help.",
                    Choice
                      "Brouwer: Hmmm. What with? Is it mysterious?"
                      [ ("Ooh yes, very. And dangerous.", Action "Brouwer: I'm in!" (add ["Luitzen Brouwer"] . removeHere ["Luitzen Brouwer"]))
                      ]
                  )
                ]
            )
            (end "Nothing")
        ),
        ( ["David Hilbert"],
          Branch
            (not . isconn 2 3)
            ( let intro = "You wait your turn in the queue. The host, David Hilbert, puts up the first guest in Room 1, and points the way to the stairs.\n\nYou seem to hear that the next couple are also put up in Room 1. You decide you must have misheard. It is your turn next.\n\nHilbert: Lodging and breakfast? Room 1 is free."
                  re1 = ("Didn't you put up the previous guests in Room 1, too?", Choice "Hilbert: I did. But everyone will move up one room to make room for you if necessary. There is always room at the Hilbert Hotel & Resort." [("But what about the last room? Where do the guests in the last room go?", Choice "Hilbert: There is no last room. There are always more rooms." [("How can there be infinite rooms? Is the hotel infinitely long?", Choice "Hilbert: No, of course not! It was designed by the famous architect Zeno Hadid. Every next room is half the size of the previous." [re2])])])
                  re2 = ("Actually, I am looking for someone.", Action "Hilbert: Yes, someone is staying here. You'll find them in Room n+1. Through the doors over there, up the stairs, then left." (updateMap (connect 2 3)))
               in Choice intro [re1, re2]
            )
            (end "Hilbert seems busy. You hear him muttering to himself: Problems, problems, nothing but problems. You decide he has enough on his plate and leave.")
        ),
        ( ["William Howard"],
          Branch
            (isAt 3 "William Howard")
            (Choice "Howard: Yes? Are we moving up again?" [("Quick, we need your help. We need to travel to Error.", Action "Howard: Fine. My bags are packed anyway, and this room is tiny. Let's go!" (add ["William Howard"] . removeAt 3 ["William Howard"]))])
            ( Branch
                (isAt 6 "William Howard")
                ( Choice
                    "Howard: What can I get you?"
                    [ ("The Lambda Rogan Josh with the Raita Monad for starter, please.", end "Coming right up."),
                      ("The Vindaloop with NaN bread on the side.", Choice "Howard: It's quite spicy." [("I can handle it.", end "Excellent.")]),
                      ("The Chicken Booleani with a stack of poppadums, please.", end "Good choice.")
                    ]
                )
                (end "Howard: We need to find Curry. He'll know the way.")
            )
        ),
        ( ["Jean-Yves Girard"],
          Branch (isconn 4 5) (end "You have seen enough here.") (Action "Raised on a large platform in the centre of the temple, Girard is preaching the Linearity Gospel. He seems in some sort of trance, so it is hard to make sense of, but you do pick up some interesting snippets. `Never Throw Anything Away' - you gather they must be environmentalists - `We Will Solve Church's Problems', `Only This Place Matters'... Perhaps, while he is speaking, now is a good time to take a peek behind the temple..." (updateMap (connect 4 5)))
        ),
        ( ["Vending machine"],
          Choice
            "The walls of the Temple of Linearity are lined with vending machines. Your curiosity gets the better of you, and you inspect one up close. It sells the following items:"
            [ ("Broccoli", end "You don't like broccoli."),
              ("Mustard", end "It might go with the broccoli."),
              ("Watches", end "They seem to have a waterproof storage compartment. Strange."),
              ("Camels", end "You don't smoke, but if you did..."),
              ("Gauloises", end "You don't smoke, but if you did...")
            ]
        ),
        ( ["Jean-Louis Krivine"],
          end "Looking through the open kitchen door, you see the chef doing the dishes. He is rinsing and stacking plates, but it's not a very quick job because he only has one stack. You also notice he never passes any plates to the front. On second thought, that makes sense - it's a takeaway, after all, and everything is packed in cardboard boxes. He seems very busy, so you decide to leave him alone."
        ),
        ( ["Haskell Curry"],
          Branch
            (isAt 6 "Haskell Curry")
            ( Choice
                "Curry: What can I get you?"
                [ ("The Lambda Rogan Josh with the Raita Monad for starter, please.", end "Coming right up."),
                  ("The Vindaloop with NaN bread on the side.", Choice "Curry: It's quite spicy." [("I can handle it.", end "Excellent.")]),
                  ("The Chicken Booleani with a stack of poppadums, please.", end "Good choice."),
                  ("Actually, I am looking for help getting to Error.", end "Curry: Hmm. I may be able to help, but I'll need to speak to William Howard.")
                ]
            )
            (end "Nothing")
        ),
        ( ["Haskell Curry", "William Howard"],
          Branch (not . isconn 6 7) (Action "Curry:  You know the way to Error, right?\nHoward: I thought you did?\nCurry:  Not really. Do we go via Computerborough?\nHoward: Yes, I think so. Is that along the I-50?\nCurry:  Yes, third exit. Shall I go with them?\nHoward: Sure. I can watch the shop while you're away." (add ["Haskell Curry"] . removeAt 6 ["Haskell Curry"] . addAt 6 ["William Howard"] . remove ["William Howard"] . updateMap (connect 6 7))) (end "It's easy, just take the third exit on I-50.")
        ),
        (["Gottlob Frege"], end "A person who appears to be the leader of the mob approaches your vehicle. When he gets closer, you recognise him as Gottlob Frege. You start backing away, and he starts yelling at you.\n\nFrege: Give us the Loop! We can control it! We can wield its power!\n\nYou don't see a way forward. Perhaps Russell has a plan."),
        ( ["Bertrand Russell", "Gottlob Frege", "Luitzen Brouwer"],
          let intro = "Frege is getting closer, yelling at you to hand over the Loop, with the mob on his heels, slowly surrounding you. The tension in the car is mounting. But Russell calmly steps out to confront Frege.\n\nRussell:"
              re1 = ("You cannot control its power! Even the very wise cannot see all ends!", Choice "Frege: I can and I will! The power is mine!\n\nRussell:" [re2, re3])
              re2 = ("Brouwer, whom do you shave?", Choice "Brouwer: Those who do not shave themselves. Obviously. Why?\n\nRussell:" [re3])
              re3 =
                ( "Frege, answer me this: DOES BROUWER SHAVE HIMSELF?",
                  Action
                    "Frege opens his mouth to shout a reply. But no sound passes his lips. His eyes open wide in a look of bewilderment. Then he looks at the ground, and starts walking in circles, muttering to himself and looking anxiously at Russell. The mob is temporarily distracted by the display, uncertain what is happening to their leader, but slowly enclosing both Frege and Russell. Out of the chaos, Russell shouts:\n\nDRIVE, YOU FOOLS!\n\nYou floor it, and with screeching tires you manage to circle around the mob. You have made it across.\n\nEND OF ACT 1. To be continued..."
                    (const Over)
                )
           in Choice intro [re1, re2, re3]
        ),
        ( ["Bertrand Russell", "Haskell Curry", "Luitzen Brouwer"],
          Branch ((== 7) . here) (end "Road trip! Road trip! Road trip!") (end "Let's head for Error!")
        )
      ]
