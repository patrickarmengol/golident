from golident import Golident

# seed = "asdfqwer"
#
# example_32 = Golident(seed, size=32, iterations=80, num_colors=5)
# example_32.save_identicon(f"img/{seed}_32.png", 8)
# example_32.show_identicon(8)
# example_32.save_history(f"img/{seed}_32.mp4")
#
# example_128 = Golident(seed, size=128, iterations=320, num_colors=5)
# example_128.save_identicon(f"img/{seed}_128.png", 2)
# example_128.show_identicon(2)
# example_128.save_history(f"img/{seed}_128.mp4")


for i in range(1, 11):
    seed = "p" * i
    g = Golident(seed, size=128, iterations=320, num_colors=5)
    # g.show_identicon()
    g.save_identicon(f"img/{i:02d}.png")
