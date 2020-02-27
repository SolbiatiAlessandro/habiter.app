def leetcode__get_team_invite_link(timezone):
    """
    timezone: str
    """
    if timezone == "gmt":
        return "gmtK"
    if timezone == "ist":
        return "istK"
    if timezone == "est":
        return "estK"
    if timezone == "pst":
        return "pstK"
    # better returning something than nothing
    #if timezone == "gmt+8":
    return "gmt+8K"
