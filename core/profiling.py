import pstats

def profile():
    p = pstats.Stats('profile_output')
    p.sort_stats('cumulative').print_stats(20)

if __name__ == "__main__":
    profile()