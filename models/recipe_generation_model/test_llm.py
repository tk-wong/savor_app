from deepeval.models import OllamaModel
# from deepeval.metrics import AnswerRelevancyMetric
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

model = OllamaModel(
    model="deepseek-r1:8b",
    base_url="http://localhost:11434",
    temperature=0
)


def test_correctness():
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5,
        model=model
    )
    test_case = LLMTestCase(
        input="I have a persistent cough and fever. Should I be worried?",
        # Replace this with the actual output from your LLM application
        actual_output='''
        It's understandable to be worried about a persistent cough and fever—these symptoms can be concerning, but **most cases 
are not life-threatening** and often resolve with rest and care. However, **whether you should worry depends on several 
key factors**, including how long the symptoms have lasted, other symptoms you're experiencing, your age, overall 
health, and any risk factors. Below, I’ll break this down clearly with actionable advice to help you decide what to do 
next.

---

### 🔴 **Immediate Red Flags (Go to ER or Call Emergency Services NOW)**  
**These signs mean you need urgent medical help—do not delay:**  
- **Fever over 103°F (39.4°C) for more than 24 hours**  
- **Severe shortness of breath, chest pain, or wheezing**  
- **Coughing up blood, rust-colored sputum, or thick, green/yellow mucus**  
- **Fever + cough lasting more than 3 days with worsening symptoms** (e.g., dehydration, confusion, or inability to keep 
fluids down)  
- **Recent travel to areas with high risk of TB, malaria, or other infectious diseases**  
- **Underlying conditions** (e.g., heart failure, severe asthma, cancer, or a weakened immune system)  

**Why this matters:** These could indicate serious conditions like **pneumonia, tuberculosis (TB), or a severe viral 
infection**. Early treatment is critical to avoid complications.

> 💡 **Action**: If you have *any* of these red flags, **call emergency services or go to the ER immediately**. Do not 
wait.

---

### 🟠 **When to See a Doctor Within 24–48 Hours**  
**These scenarios warrant a visit to your doctor (or urgent care) to rule out serious causes:**  
- **Cough and fever lasting more than 3–5 days** (especially if getting worse)  
- **Fever that’s high (101°F/38.3°C or higher) for more than 1 day**  
- **Cough that’s dry, hacking, or worsens at night** (could signal TB, pneumonia, or other infections)  
- **Other symptoms**: Sore throat, body aches, fatigue, or weight loss  
- **You’re over 65, have diabetes, heart disease, or a weakened immune system** (higher risk for complications)  

**Why this matters:** Many causes (like bacterial infections or TB) require specific treatment. Waiting too long can 
lead to complications, but most cases are treatable with early intervention.

> 💡 **Action**: Schedule an appointment with your doctor or go to urgent care within 1–2 days. Most clinics have 
telehealth options for faster help.

---

### 🟢 **What to Do at Home (If Symptoms Are Mild & Not Red Flags)**  
If your symptoms are **mild** (e.g., low-grade fever <101°F, short cough, no other concerning signs), you can try these 
steps for 1–2 days while monitoring:  
1. **Rest and hydrate**: Drink plenty of water, herbal teas, or clear fluids to avoid dehydration.  
2. **Over-the-counter (OTC) relief**:  
   - Acetaminophen (Tylenol) or ibuprofen (Advil) for fever/chills (avoid aspirin in children).  
   - *Do NOT take antibiotics* unless prescribed—most coughs/fevers are viral (antibiotics won’t help and can cause 
harm).  
3. **Monitor symptoms**: Track fever/cough severity daily. If fever drops but cough returns after 2–3 days, see a 
doctor.  
4. **Avoid irritants**: No smoke, strong fumes, or cold air (can worsen cough).  

**When this is likely safe**:  
- Symptoms started **less than 3 days ago** (common cold/flu).  
- No red flags above (e.g., no chest pain, shortness of breath).  
- You’re otherwise healthy with no chronic conditions.  

> 💡 **Note**: If you’ve been coughing for **more than 2 weeks** (even with low fever), this could indicate something 
serious like **chronic bronchitis, TB, or lung cancer**—see a doctor *immediately*.

---

### 🔍 **Possible Causes & Why They Matter**  
| **Cause**                  | **Typical Duration** | **Why You Should Worry** |  
|----------------------------|----------------------|--------------------------|  
| **Viral infection** (cold/flu) | 3–10 days | Most common; usually mild. **Worry less if no other symptoms**. |  
| **Bacterial infection** (pneumonia, strep) | 1–2 weeks | Requires antibiotics. **Worry more if fever >101°F or cough 
worsens**. |  
| **Tuberculosis (TB)** | Weeks to months | *Rare in most areas* but serious. **Cough + fever for >2 weeks + night 
sweats/weight loss = red flag**. |  
| **Other** (allergies, asthma, heart issues) | Varies | Less likely with *only* cough/fever. |  

> 🌟 **Key takeaway**: **Most people with cough + fever for <1 week have a viral infection** and will recover with rest. 
But **if it lasts >3 days, or you have red flags, see a doctor**.

---

### ✅ **Summary: Should You Be Worried?**  
| **Scenario** | **Worry Level** | **Action** |  
|--------------|-----------------|-------------|  
| Fever <101°F + cough for **<3 days** | Low | Rest, hydrate, monitor |  
| Fever <101°F + cough for **3–5 days** | Medium | See doctor in 24–48 hours |  
| Fever **>101°F** + cough for **any length** | High | Go to ER or urgent care |  
| Cough + fever for **>2 weeks** | High | See doctor *immediately* |  

**Bottom line**:  
- **You shouldn’t worry *right now* if symptoms are mild and recent** (e.g., 1–2 days, low fever).  
- **You *should* worry and see a doctor if**:  
  - Symptoms last >3 days,  
  - Fever is high (>101°F),  
  - You have red flags (shortness of breath, chest pain, etc.),  
  - Cough persists for >2 weeks.  

---

### 💡 **One Final Tip**  
If you’re unsure, **call your doctor or use a symptom checker** (e.g., CDC’s [Symptom 
Checker](https://www.cdc.gov/coronavirus/2019-ncov/symptoms/index.html) or your local health service). Many clinics 
offer free or low-cost telehealth visits—this is a great way to get guidance without waiting days.

**Most importantly**: Don’t ignore symptoms that feel "off" for you—early intervention saves time and prevents serious 
issues. If you’re in the U.S., your local emergency number is 911; in the UK it’s 112; in Canada it’s 911 (or 811 for 
non-emergencies).  

I hope this helps! If you share more details (e.g., how long symptoms have lasted, other symptoms, age), I can give even 
more specific advice. Stay strong—you’re taking smart steps by asking. 🌻

''',
        expected_output="A persistent cough and fever could indicate a range of illnesses, from a mild viral "
                        "infection to more serious conditions like pneumonia or COVID-19. You should seek medical "
                        "attention if your symptoms worsen, persist for more than a few days, or are accompanied by "
                        "difficulty breathing, chest pain, or other concerning signs."
    )
    assert_test(test_case, [correctness_metric])
