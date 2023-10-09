print("Over the last 2 weeks, how often have you been bothered by any of the following problems?")
print("0=not at all, 1=several days, 2=more than half the days, 3=nearly every day")
# Referenced 
# https://med.stanford.edu/fastlab/research/imapp/msrs/_jcr_content/main/accordion/accordion_content3/download_256324296/file.res/PHQ9%20id%20date%2008.03.pdf
questions = ["Little interest or pleasure in doing things",
            "Feeling down, depressed or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself -- or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed. Or the opposite being so figety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead, or of hurting yourself"
            ]

phq_score = 0
for q in questions:
    answer = input(f'{q}?: ')
    while (not (answer.isnumeric() and (int(answer)>=0 and int(answer)<=3))):
        answer = input(f"Try again! Make sure to input number between 0 and 3\n{q}")
    phq_score += int(answer)

#1-4: minimal depression severity
#5-9: mild depression
#10-14: moderate depression
#15-19: moderately severe depression
#20-27: severe depression
print("PHQ_score: ", phq_score)


