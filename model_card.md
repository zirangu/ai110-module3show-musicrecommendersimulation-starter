# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

**Plain-language explanation:**

Think of each song as a point with four "audio dials" turned somewhere between 0 and 1: how energetic it is, how positive/upbeat it sounds, how danceable it is, and how acoustic (unplugged) it feels. When you tell the system what you're in the mood for, it sets those same four dials to your target, then checks every song in the catalog and measures how close its dials are to yours — the closer the dials line up, the higher the "audio match" score it gets.

On top of that base match, the system gives two small bonuses: a bigger one if the song's mood label (like "chill" or "happy") matches what you asked for, since mood is the clearest hint of what you want to hear right now, and a smaller one if the song's genre is one you said you like, since genre is more about general taste than the specific moment. A song still needs a genuinely close audio match to rank near the top — the bonuses only help break ties or nudge close calls, they can't rescue a song whose overall vibe is far off from what you asked for. Finally, the system sorts every song by its total score and hands back the highest-scoring ones, along with a plain-English reason for each (e.g., "it's a 95% audio match, and it matches your happy mood").

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
