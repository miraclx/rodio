def function(count):
    count += 1
    print(f"function! count -> {count}")
    function(count)


function(0)

# This results to a stack overflow
# Because of continuous nested calling of itself
