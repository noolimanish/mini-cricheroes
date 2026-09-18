class Player:
    
    VALID_ROLES = {"batsman", "bowler", "all-rounder"}
            #BOWLING_TYPES = {"seam", "spin"}
            #SPIN_STYLES = {"right-arm-off-break","right-arm-leg-break","left-arm-orthodox","left-arm-wrist-spin",}
            #SEAM_STYLES = {"right-arm-fast","right-arm-fast-medium","right-arm-medium-fast","right-arm-medium","left-arm-fast","left-arm-fast-medium","left-arm-medium-fast","left-arm-medium",}
    VALID_BOWLING_STYLES = {
                "seam": { "right-arm-fast","right-arm-fast-medium","right-arm-medium-fast","right-arm-medium",
                    "left-arm-fast","left-arm-fast-medium","left-arm-medium-fast","left-arm-medium", },
                "spin": { "right-arm-off-break","right-arm-leg-break","left-arm-orthodox","left-arm-wrist-spin", }
                            }
            
    def __init__(self, name, email, role, batting_style,bowling_type=None,bowling_style=None):
        normalized_role = role.lower().replace(" ", "-")
        normalized_bowling_type = bowling_type.lower() if bowling_type else None
        normalized_bowling_style = bowling_style.lower() if bowling_style else None
        
        self.name = name
        self.email = email 
        self.role= normalized_role
        self.batting_style = batting_style
        self.bowling_type = bowling_type
        self.bowling_style = bowling_style

        if normalized_bowling_type is not None and normalized_bowling_type not in self.VALID_BOWLING_STYLES:
            raise ValueError("Invalid bowling type. Choose 'seam' or 'spin'.")
        if normalized_bowling_type is not None and normalized_bowling_style is not None:
            if normalized_bowling_style not in self.VALID_BOWLING_STYLES[normalized_bowling_type]:
                raise ValueError(f"Invalid bowling style for {normalized_bowling_type}.")

        if normalized_role not in self.VALID_ROLES:
            raise ValueError("Invalid role. Choose Batsman, Bowler, or All-rounder.")

        if normalized_role == "bowler" and bowling_style is None:
            raise ValueError("Bowler should have a bowling style.")

        if normalized_role == "all-rounder" and (batting_style is None or bowling_style is None):
            raise ValueError("All-rounder should have both batting and bowling styles.")

        if normalized_role == "batsman" and batting_style is None:
            raise ValueError("Batsman should have a batting style.")
        
    def display_info(self):
        print(f"Name: {self.name}")
        print(f"Email: {self.email}")
        print(f"Role: {self.role}")
        print(f"Batting Style: {self.batting_style}")
        print(f"Bowling Style: {self.bowling_style}")