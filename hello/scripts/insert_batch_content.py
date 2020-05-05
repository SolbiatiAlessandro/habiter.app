from hello.habiterDB import add_community_content_item
import pickle as pkl

if __name__ == "__main__":
    print("Hi! I can insert batch content from a pickle file. I need three things")
    print("\n1) pickle filename that contains {'links': ['link1', 'link2']}")
    filename = input()
    links = pkl.load(open(filename, "rb"))['links']
    print("\nok, I retrieved "+str(len(links))+" links, \
            the first one is "+links[0]+\
            "and the last one is "+links[-1])
    print("\n2) community name (e.g. Leetcode)")
    community = input()
    print("\n3) label (e.g. beginner)")
    label = input()
    print("\ncool, I will insert the content in the prod database..")
    failed = 0
    for link in links:
        try:
            add_community_content_item(
                    link,
                    label,
                    community
                    )
            print("SUCCESS:")
        except Exception as e:
            print("FAILURE:")
            print(e)
        print(link, label, community)
    print("\n\n\n FINISHED. {} SUCCESS and {} FAILURE".format(
        str(len(links)-failed),
        str(failed)
        ))
