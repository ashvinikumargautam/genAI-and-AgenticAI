import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")
text = "hey there! my name is piyush garg"
print(f"input text : {text}")
tokens = enc.encode(text)
# [48467, 1354, 0, 922, 1308, 382, 173566, 1776, 84534]
print("Tokens : ", tokens)
decoded = enc.decode([48467, 1354, 0, 922, 1308, 382, 173566, 1776, 84534])
print("decoded : ",decoded)