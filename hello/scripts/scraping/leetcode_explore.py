def get_raw_titles(raw_html):
    """
    returns ['Best Time to Buy and Sell Stock II', ... ] 
    """
    SEARCH = "<span title=\""
    curr = raw_html.find(SEARCH)
    titles = []
    while curr != -1 and curr < len(raw):
        start =  curr + len(SEARCH)
        end = start + raw_html[start:].find("\"")
        titles.append(raw_html[start:end])
        curr = end + raw_html[end:].find(SEARCH)
    return titles

def gen_urls(raw_html):
    """
    returns
    ['https://leetcode.com/problems/remove-duplicates-from-sorted-array', ... ]
    """
    return [*map(lambda x: 
            "https://leetcode.com/problems/"+\
                    x.\
                    lower().\
                    replace(" ", "-").\
                    replace("(", "").\
                    replace("'", "").\
                    replace(")", ""),
            get_raw_titles(raw_html))]
