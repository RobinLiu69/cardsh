import random, os
from typing import Any, Iterable, Sequence, Collection

FOLDER_PATH = os.path.realpath(os.path.dirname(__file__))

def value_is_int(v: str) -> bool:
    return v.replace("-", "").isdigit() and v.count("-") <= 1 and (v.count("-") == 0 or v[0] == "-")

def get_indices(lst: Sequence[Any], targets: Sequence[Any]) -> list[int]:
    return list(filter(lambda x: (lst[x]) in targets, range(len(lst)))) # type: ignore

def get_elements(lst: Sequence[Any], targets: Sequence[Any]) -> list[Any]:
    return list(filter(lambda x: x in targets, lst))

def delete_elements(lst: list[Any], targets: Sequence[Any], start: int=0, end: int=-1, step: int=1) -> list[Any]:
    deleteIdices = sorted(get_indices(lst[start:end:step], targets), reverse=True)
    for i in deleteIdices:
        if step == -1:
            lst.pop(-1-i) 
        else:
            lst.pop(i)
    return lst

class Player():
    def __init__(self, name:str) -> None:
        self.name = name
        self.deck: list[str] = []
        self.hand: list[str] = []
        self.graveyard: list[str] = []
        self.in_play: list[str] = []
        self.shuffle_pile: list[str] = []
        self.discard_pile: list[str] = []

    def load_deck(self) -> None:
        with open(f"{FOLDER_PATH}/{self.name}.txt", 'r', encoding='utf-8') as file:
            self.deck = [line.strip() for line in file.readlines()]
        self.shuffle_pile.extend(self.deck)
        random.shuffle(self.shuffle_pile)

    def draw_card(self) -> str | None:
        if self.shuffle_pile:
            card = self.shuffle_pile.pop()
            self.hand.append(card)
            print(f"抽到的牌:{card}")
            return card
        else:
            self.shuffle_pile.extend(self.discard_pile)
            self.discard_pile = []
            random.shuffle(self.discard_pile)
            if self.shuffle_pile:
                card = self.shuffle_pile.pop()
                self.hand.append(card)
                print(f"抽到的牌:{card}")
                return card
            else:
                print(f"無效動作: 牌堆已空")
                return None

    def use_card(self, card_source_name: str, card_source: list[str], card_destination_name: str, card_destination: list[str]) -> bool:
        print("\n"*3+f"{card_source_name}:", self.display_carddeckInfo(card_source))
        index = input("\n"*5+"使用的牌:")
        
        if value_is_int(index) and -len(card_source) < int(index) < len(card_source):
            card_destination.append(card_source.pop(int(index)))
            return True
        else:
            if index == "" and len(card_source):
                index = input("再按一次ENTER則自動使用最後一張牌 其餘則退出")
                if index == "":
                    card_destination.append(card_source.pop(int(-1)))
                    return True
                else:
                    print("退出")
                    return False
            else:
                print("無效動作")
                return False
    
    def select_card_from_disorder_pile(self, card_source_name: str, card_source: list[str], card_destination_name: str, card_destination: list[str], all: bool=False) -> bool:
        tempShuffle = list(set(card_source))
        print("\n"*3+f"{card_source_name}(無序):", self.display_carddeckInfo(tempShuffle))
        index = input("\n"*5+"使用的牌(若該牌堆中有超過一張同名的卡則隨機拿走一張):" if not all else "\n"*5+f"使用的牌({card_source_name}中同名的卡都會拿走):")
        
        if value_is_int(index) and -len(tempShuffle) < int(index) < len(tempShuffle):
            if all:
                card = tempShuffle[int(index)]
                card_destination += get_elements(card_source, (card))
                delete_elements(card_source, (card))
            else:
                card = tempShuffle[int(index)]
                card_destination.append(card_source.pop(random.choice(get_indices(card_source, (card)))))
            return True
        else:
            print("無效動作")
            return False
    
    def select_card_from_ordered_pile(self, card_source_name: str, card_source: list[str], card_destination_name: str, card_destination: list[str], reveal: int=-1, all: bool=False) -> bool:
        reveal = reveal if reveal != -1 else len(card_source)
        tempShuffle = card_source[len(card_source)-1:len(card_source)-1-reveal:-1]
        print("\n"*3+f"{card_source_name}(前{reveal}張):", self.display_carddeckInfo(tempShuffle))
        index = input("\n"*5+"使用的牌:" if not all else "\n"*5+f"使用的牌({card_source_name}中前{reveal}張同名的卡都會拿走):")
        
        if value_is_int(index) and -len(tempShuffle) < int(index) < len(tempShuffle):
            if all:
                card = tempShuffle[int(index)]
                card_destination += get_elements(card_source[len(card_source)-1:len(card_source)-1-reveal:-1], (card))
                delete_elements(card_source, (card), start=len(card_source)-1, end=len(card_source)-1-reveal, step=-1)
            else:
                card_destination.append(card_source.pop(-1-int(index)))
            return True
        else:
            print("無效動作")
            return False
    
    def play_card(self) -> int:
        print(f"\n0.抽牌 1.使用牌 2.將使用的牌丟進棄牌堆 3.使用的牌丟進獻祭堆 4.將獻祭堆的牌放回手牌 5.從抽牌堆拿到手牌 6.特殊卡牌功能 exit:退出")
        action = input("輸入動作:")
        print("\n"*3)

        match action:
            case "0":
                self.draw_card()
                
            case "1":
                self.use_card("手牌", self.hand, "場上堆", self.in_play)
                
            case "2":
                self.use_card("場上堆", self.in_play, "棄牌堆", self.discard_pile)

            case "3":
                self.use_card("場上堆", self.in_play, "獻祭堆", self.graveyard)
                
            case "4":
                self.use_card("獻祭堆", self.graveyard, "手牌", self.hand)

            case "5":
                self.select_card_from_disorder_pile("抽牌堆", self.shuffle_pile, "手牌", self.hand)

            case "6":
                self.special_card()

            case "exit":
                return 0

            case _:
                print("無效動作")
        
        self.display_status()
        return 1
    
    def special_card(self) -> bool:
        self.display_status()
        print(f"\n0.從棄牌堆拿到手牌 1.強充能(刪掉) exit:退出")
        action = input("輸入動作:")
        print("\n"*3)
        
        match action:
            case "0":
                self.use_card("棄牌堆", self.discard_pile, "手牌", self.hand)
                
            case "1":
                self.select_card_from_ordered_pile("抽牌堆", self.shuffle_pile, "手牌", self.hand, reveal=5, all=True)

            case "exit":
                return False

            case _:
                print("無效動作")
        return False
    
    def display_carddeckInfo(self, lst: list[str]) -> str:
        return ", ".join(list(str(i)+"-"+v for i, v in enumerate(lst)))
    
    def display_status(self):
        print("\n")
        print("玩家名子:", self.name)
        print("抽牌堆剩於牌數:", len(self.shuffle_pile))
        print("手牌:", self.display_carddeckInfo(self.hand))
        print("\n場上堆:", self.display_carddeckInfo(self.in_play))
        print("\n棄牌堆:", " ".join(self.discard_pile))
        print("獻祭堆:", " ".join(self.graveyard))
        


def main() -> int:

    print("(請確認你角色名與你的牌堆txt檔名一樣無誤)")
    name = input("\n輸入角色1名子:")
    
    player = Player(name)
    
    try:
        player.load_deck()
    except FileNotFoundError:
        print("無法載入檔案\n(請確認你的角色名與檔名一樣)")
        return 1
        
    
    while player.play_card(): pass
    return 0
    
    
if __name__ == "__main__":
    main()