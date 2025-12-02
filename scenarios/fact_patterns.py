"""Scenario fact patterns for complaint generation."""

# =============================================================================
# QUIET ENJOYMENT (Landlord-Tenant) Scenarios
# =============================================================================

QUIET_ENJOYMENT_SCENARIOS = [
    # 1. Partial repairs / recurring problem
    """
    I rent a two-bedroom in Dorchester. Last winter my heat kept cutting out—not
    completely, but it would drop to maybe 60 degrees for a few hours at a time,
    usually in the evenings. My landlord actually did send someone out twice. The
    first time they said they fixed it, and it worked okay for about a week. Then
    it started happening again. The second repair guy said the boiler was "old but
    functional" and there wasn't much more to do.

    So technically repairs were made, but the problem keeps coming back. I had to
    buy two space heaters to keep the place livable, which ran up my electric bill
    by about $150 a month. I also got bronchitis in January that my doctor said was
    probably made worse by the cold indoor air—I missed three days of work and had
    to pay for antibiotics. My landlord says the heat is "working" because it never
    goes completely out and the building isn't freezing.
    """,
    # 2. Tenant was late on rent / retaliatory timing question
    """
    I live in a basement unit in Roxbury. I'll be honest—I was about two weeks late
    on rent in October because I had some medical bills. I paid it all eventually
    with the late fee. Then in November, I noticed water seeping in through the
    basement wall whenever it rained hard. I texted my landlord about it and she
    said she'd "look into it."

    A few weeks later, nothing had been done, so I called the city. They came out
    and found the water issue plus some other code stuff. The water ruined a rug
    and damaged a bookshelf I had against that wall—probably $400 worth of stuff.
    I've also had to run a dehumidifier constantly, which has added to my electric
    bill. Now my landlord is saying I'm a "problem tenant" and that she's not going
    to renew my lease when it's up in March. She says it's because of the late rent,
    not the inspection, but the timing seems suspicious. The water problem still
    isn't fixed either.
    """,
    # 3. Pre-existing condition / knew before moving in
    """
    I moved into a studio in Jamaica Plain about eight months ago. During the
    showing, I noticed some water stains on the ceiling and asked about them. The
    landlord said it was from an old leak that had been "totally fixed." I took
    his word for it.

    Well, the first big rainstorm, water started dripping through in the exact same
    spot. I've complained multiple times but my landlord keeps saying it's a "minor
    cosmetic issue" and that I knew the apartment had "character" when I signed the
    lease. The dripping has gotten worse—during one storm it soaked my couch and
    ruined a laptop I'd left on the coffee table, which cost me about $900 to replace.
    Now there's a musty smell and I've been getting headaches that I think are from
    mold. I had to move my bed away from that area and I'm basically living in half
    the apartment.
    """,
    # 4. Landlord disputes severity
    """
    I rent a place in Worcester and started noticing mouse droppings in my kitchen
    about three months ago. I told my landlord and he put out a few traps. We caught
    maybe two mice but I'm still finding droppings regularly. My landlord says this
    is "normal for older buildings" and that I need to keep my kitchen cleaner—which
    honestly feels insulting because I keep things pretty spotless.

    He did hire an exterminator once, but just for a single visit. The exterminator
    told me the building probably needs more comprehensive treatment, but my landlord
    says that's overkill and too expensive. I've had to throw away a lot of food—
    anything in boxes or bags that wasn't sealed—probably $200 worth over the past
    few months. I also bought plastic containers for everything, which cost another
    $80 or so. I'm constantly anxious about cooking or eating in my own kitchen. So
    we're at a standoff—he thinks he's done enough, but I'm still finding droppings
    every week.
    """,
    # 5. Ambiguous "substantial interference" / noise from neighboring unit
    """
    I live on the second floor of a triple-decker in Somerville. The people above
    me moved in about six months ago and they're incredibly loud—stomping around
    at all hours, playing music late, what sounds like furniture moving at midnight.
    I've asked them directly to keep it down and they did for maybe a week, then
    went right back to it.

    I've complained to my landlord probably five or six times. He talked to them
    once and said he "can't control how people live." My lease says I'm entitled to
    "quiet enjoyment" and we all share the same landlord. I'm averaging maybe four
    or five hours of sleep a night because of the noise. I got a written warning at
    work for falling asleep at my desk, and my doctor has me on sleep medication now
    that costs me $40 a month. I bought earplugs, a white noise machine, even tried
    rearranging my bedroom—nothing helps.
    """,
    # 6. Timeline issues / how long is too long
    """
    The hot water in my apartment in Brockton went out about three weeks ago. I
    reported it to my landlord the same day. He said the water heater needed a part
    and he ordered it. A week later, still no hot water. He said the part was
    backordered. Another week, same story.

    Now it's been three weeks of cold showers and boiling water to wash dishes. I've
    been going to the gym just to shower, which costs me $30 a month I wasn't paying
    before, plus gas to get there. I also had to take my baby to my mother's house
    for baths because I can't bathe her in cold water. My landlord keeps saying he's
    "working on it" and that he can't make the supplier ship faster. He's not ignoring
    me exactly—he responds to my texts and seems to be trying—but I still don't have
    hot water and it's been almost a month.
    """,
    # 7. Construction disruption but temporary
    """
    My landlord is renovating the unit next to mine in Cambridge. For the past
    two months there's been construction noise during the day—drilling, hammering,
    workers talking loudly. It usually runs from about 8 AM to 5 PM on weekdays.
    I work from home and it's made it really hard to concentrate on calls.

    The thing is, the landlord did tell me about the renovation before it started,
    and the workers do keep reasonable hours. But two months is a long time and
    they're saying it might be another month or two. Dust gets into my unit through
    the vents sometimes. My landlord offered me a small rent reduction—like $100
    off one month—but that doesn't really make up for how disruptive this has been.
    """,
    # 8. Security/safety concern but no actual incident
    """
    The main entry door to my building in Chelsea has a broken lock—it doesn't
    latch properly and anyone can just push it open. I told my landlord about
    this maybe two months ago. He said he'd fix it but nothing has happened.
    I've reminded him twice since then.

    Last month someone came into the building and went through the mail—a bunch
    of us had packages stolen from the hallway. I lost a package worth about $120.
    I've also started finding evidence that someone has been sleeping in the
    basement, which is really unsettling. I bought a security camera for my own
    door and a better deadbolt, which cost me about $200. My landlord says I'm
    "overreacting" and that the neighborhood is safe, but clearly that's not true.
    """,
    # 9. Partial utility disruption
    """
    I have a two-bedroom in Springfield and one of the bedrooms has had no
    electricity for about six weeks. Something's wrong with the wiring in that
    room specifically—the outlets don't work and the overhead light is dead. The
    rest of the apartment is fine.

    My landlord sent an electrician who said it would need a bigger repair to fix
    properly. My landlord says he's getting quotes but it's "complicated" because
    of the building's old wiring. Meanwhile I can't use that room at all—I was
    using it as a home office and now I've had to work from coffee shops, spending
    maybe $15 a day on coffee and food just to have somewhere to sit. I've also
    been paying for a coworking space membership at $150 a month. All my office
    stuff is crammed into the living room, which has made the whole apartment feel
    unlivable.
    """,
    # 10. Landlord claims tenant caused the problem
    """
    There's mold growing in my bathroom in Lowell. It started in the corner of
    the shower and has spread to the ceiling. I reported it to my landlord and
    she came to look at it but then blamed me, saying I don't run the exhaust fan
    enough and I take showers that are "too hot and too long."

    I do run the fan when I shower, but maybe not every single time. And I do like
    hot showers but I don't think that's unusual. The bathroom doesn't have a window,
    just the fan. Since the mold appeared, I've been having respiratory issues—
    coughing, congestion, wheezing—that I never had before. My doctor thinks it's
    related to the mold and told me I should get it remediated. I had to throw away
    my shower curtain and some towels that got moldy, about $60 worth. My landlord
    says she'll clean the existing mold but won't do anything about the ventilation
    because I "caused" the problem.
    """,
]


# =============================================================================
# NEGLIGENCE (Personal Injury) Scenarios
# =============================================================================

NEGLIGENCE_SCENARIOS = [
    # 1. Slip on milk in grocery store - borderline on notice/time
    """
    I was shopping at a grocery store in Somerville on a Saturday afternoon. In the
    dairy aisle, I stepped into a puddle of spilled milk and went down hard on my
    hip. The puddle wasn't tiny—you could see cart tracks going through it—but there
    were no "wet floor" signs or cones anywhere.

    There was an employee stocking shelves maybe fifteen feet away. After I fell, he
    came over and said he'd noticed the spill "a few minutes ago" but was finishing
    up what he was doing before he was going to get the mop. I finished my shopping
    because I thought I was okay, but my hip really started hurting that night. I
    went to urgent care the next day, was told it was a hip sprain, and ended up
    needing physical therapy. I missed several shifts at my café job while I was
    recovering.
    """,
    # 2. Dog off leash - borderline on causation (dog didn't bite)
    """
    I was jogging in a park in Newton where there are signs saying all dogs have to
    be on leashes. There's a guy who regularly lets his big dog run around loose
    anyway. One afternoon I was running on the path and his dog suddenly charged at
    me, barking loudly. The owner was maybe thirty feet away talking with friends,
    holding the leash over his shoulder but not attached to the dog.

    I didn't know if the dog was going to bite me, so I swerved off the path to get
    away from it. I tripped over a tree root and fell down a small embankment,
    breaking my wrist. The dog never actually touched me—it stopped when I fell and
    the owner finally called it back. Several other joggers saw the whole thing
    happen. I had to go to the ER, wear a brace for weeks, and missed work and a
    piano recital I'd been practicing for.
    """,
    # 3. Box falling - borderline on foreseeability
    """
    I was in a discount home-goods store in Lowell looking at kitchen stuff. They
    had heavy boxes of appliances stacked pretty high on the shelves—maybe five or
    six boxes up—without any straps or barriers. Another customer was pushing a cart
    down the aisle and bumped one of the lower shelves, not hard, just a normal bump.

    A big toaster-oven box fell from near the top and landed on my shoulder and the
    side of my head. I got dizzy right away and had a bad headache. The manager came
    over, filled out an incident report, and offered me a store coupon. That night
    my symptoms got worse, so I went to the ER. They said I had a mild concussion
    and a shoulder strain. I'm a delivery driver and had to miss a few days of work,
    and I couldn't play in my weekly soccer league for about a month.
    """,
    # 4. Icy sidewalk - borderline on property owner's duty
    """
    There's a three-unit apartment building in Worcester where the owner is supposed
    to take care of the sidewalk. After a snowstorm in February, she shoveled a narrow
    path down the middle of the sidewalk but didn't put down any salt or sand. Over
    the next couple of days, that path turned into a sheet of ice from the melting
    during the day and refreezing at night.

    I was delivering groceries to one of the tenants and walked up the sidewalk like
    normal. I hit the ice patch, my feet went out from under me, and I fell backward,
    landing hard on my lower back. The tenants told me afterward that they had texted
    the landlord about the ice and even sent her pictures, and she told them "the sun
    will take care of it." I ended up needing treatment for my back and missed about
    a week of work.
    """,
    # 5. Neighbor's ladder - borderline on whether warning was enough
    """
    I live in a duplex in Springfield and share a driveway with my neighbor. He keeps
    a tall aluminum extension ladder leaning against the wooden fence right next to
    where I park my car. I'd mentioned to him a couple times that I was worried it
    might fall over onto my car, especially on windy days. He said he'd tie it down
    or move it but never got around to it.

    On a windy day in March, I was backing into the driveway when a gust of wind
    knocked the ladder over. It crashed onto the hood and windshield of my car,
    denting the hood and cracking the windshield. The car still ran fine but needed
    bodywork and a new windshield. I had to pay my deductible and rent a car while
    mine was in the shop for over a week.
    """,
    # 6. Bike doored - borderline on comparative fault claims
    """
    I was biking to work in Boston in a marked bike lane on a busy street, following
    traffic rules and wearing my helmet. A rideshare driver was parked in a loading
    zone right next to the bike lane, which is pretty common. Without checking his
    mirror or looking, he suddenly swung his door wide open right as I was passing.

    I had no time to stop or swerve and crashed straight into the edge of the door.
    I flew off my bike and hit the pavement. I ended up with road rash on my arms and
    legs, a chipped front tooth, and my bike frame got bent. At the scene, the driver
    admitted he "didn't see me" because he was checking his phone. But later, when I
    filed a claim with his insurance, they said he told them I was "weaving in and out
    of traffic." I wasn't. I had to pay for dental work and buy a new bike.
    """,
    # 7. Kid hurt at after-school program - borderline on supervision standard
    """
    My son goes to an after-school program at a community center in Brockton. They
    advertise that kids will be supervised at all times in the gym. One day, there
    was supposed to be two staff members watching about twenty kids, but one of them
    left to do paperwork in the office. The person who stayed was mostly looking at
    her phone near the bleachers.

    Two older boys, probably twelve or so, started playing a rough tackle game on the
    hardwood floor. A couple of other kids told the staff member but she just said
    "boys will be boys." My eight-year-old, who's small for his age, got tackled hard
    by one of the bigger kids, hit his head on the floor, and was unconscious for
    maybe thirty seconds. He ended up in the ER with a concussion, missed several
    days of school, and we're still dealing with the medical bills.
    """,
    # 8. Slip in restaurant hallway - borderline on time before cleanup
    """
    I was having dinner at a casual restaurant in Quincy. In the narrow hallway
    between the kitchen and the dining room, a server dropped a tray with several
    water glasses. She picked up the broken glass quickly but left the water and
    ice on the tile floor, saying she'd "be right back with a mop." She didn't put
    down any wet floor sign or warning.

    About ten minutes later, I got up to use the bathroom. The hallway was still
    wet—I could see the water glistening but thought it was just shiny tile until
    I was already stepping on it. I slipped and twisted my knee badly. Afterward,
    I overheard other staff members saying they'd been "dodging that puddle" for
    a while. I went to urgent care, was told I had a sprained knee, and ended up
    in a brace and physical therapy for weeks.
    """,
    # 9. Smoke detector without battery - borderline on causation of injuries
    """
    I live on the third floor of a small apartment building in Lynn. The landlord
    is supposed to maintain smoke detectors in the common hallways. For months, the
    detector right outside my unit was chirping because of a low battery. Eventually
    someone—I don't know who—just took the battery out to stop the noise and left
    it sitting on the windowsill. I told the landlord about it at least three times,
    and he kept saying he'd "take care of it."

    One night, a fire started in a first-floor apartment—something in their kitchen.
    Because the hallway detector had no battery, we got no warning upstairs. I only
    realized something was wrong when I smelled smoke, and by then the hallway was
    already thick with it. I had trouble breathing while trying to get out and spent
    the night in the hospital with smoke inhalation. A lot of my belongings were also
    damaged by smoke and water.
    """,
    # 10. Tree branch falling - borderline on constructive notice
    """
    I often walk on a residential street in Pittsfield where there's a big old maple
    tree in front of one of the houses. For a long time, one of the major branches
    hanging over the sidewalk looked cracked and droopy. I'd noticed it myself, and
    neighbors told me they'd mentioned it to the homeowner and suggested he get it
    checked by an arborist. He told them he'd "deal with it in the spring" but
    never did.

    During a fairly normal summer thunderstorm—nothing extreme, no tornado warnings
    or anything—that cracked branch finally snapped and fell right as I was walking
    by with grocery bags. It landed on my shoulder and back and knocked me to the
    ground. I ended up with a shoulder strain and a lot of bruising, had to get
    medical treatment, and missed about a week of my retail job.
    """,
]


# =============================================================================
# CUSTODY MODIFICATION Scenarios
# =============================================================================

CUSTODY_MODIFICATION_SCENARIOS = [
    # 1. Ex's new night shift - borderline on what constitutes "material change"
    """
    A few years ago, the court set up a parenting schedule for our two kids. I have
    them most of the time, and their dad gets them every other weekend plus one
    overnight during the week. Back when we made that arrangement, we both worked
    regular daytime jobs, so the schedule made sense.

    Recently my ex took a new job working 7 PM to 7 AM several nights a week,
    including many of the nights he's supposed to have the kids overnight. He's been
    dropping them off at my place with almost no notice because he says he's too tired
    to watch them after his shift, or he leaves them with his roommate, who I barely
    know. The kids tell me they often fall asleep on the couch while he naps after
    getting home from work. I want to change the schedule so overnights only happen
    when he's actually off work and available.
    """,
    # 2. Ex moving out of state - borderline on whether distance alone is enough
    """
    Right now I have primary custody of our daughter, and her dad has her on
    Wednesdays and every other weekend based on a court order from when we both
    lived in the Cambridge area. The whole arrangement assumes we all live close
    by and our daughter goes to the local school.

    My ex now wants to move to New Hampshire for a job opportunity and still keep
    the exact same schedule. That would mean our daughter doing long drives—around
    ninety minutes each way in traffic—for midweek overnights, then getting up
    super early to get back to school the next morning. She's already started getting
    anxious about these drives and missing her after-school activities. I'm asking
    to remove the midweek overnight and adjust the weekend schedule to something
    that actually works with the distance.
    """,
    # 3. Substance-use concerns - borderline on whether evidence is enough
    """
    Two years ago the court gave us shared legal custody. My son lives with me most
    of the time, and he goes to his other parent's place on certain weekends. At
    the time of that order, the judge thought we were both stable and could co-parent
    without problems.

    Lately my son has been telling me things that worry me. He says there are "special
    drinks" at his other parent's house and that sometimes that parent "can't walk
    straight." A neighbor who knows our situation sent me a video of my ex stumbling
    while getting our son out of the car late at night. The school has also mentioned
    that my son seems exhausted every Monday morning. I want to change the order so
    that overnights are supervised or at least have some conditions, because I'm
    genuinely worried about his safety over there.
    """,
    # 4. Kid is older, schedule hasn't grown with him - mutual modification
    """
    When our son was three years old, the court gave me primary physical custody and
    gave his dad three short visits during the week plus a Sunday afternoon—but no
    overnights—because his dad only had a room in a shared apartment with roommates
    and no real space for a child.

    Now our son is eight, in school full time, and keeps asking for actual sleepovers
    at his dad's place. His dad now has his own apartment where our son has his own
    bedroom. With the current schedule, our son is constantly being shuttled back and
    forth for short visits on school nights, which is exhausting for everyone and
    makes homework and bedtime routines difficult. His dad and I both agree the
    schedule needs to change to fit his age and school life better.
    """,
    # 5. Other parent undermining relationship - borderline on proving harm
    """
    Our current court order says we share legal custody. The kids live with me most
    of the time and go to their other parent's house on a regular schedule. The order
    also says we're supposed to support the kids' relationship with each parent and
    not disparage each other in front of them.

    Over the past year, my ex has been signing the kids up for activities that fall
    during my scheduled weekends without discussing it with me first, then telling
    them it's my fault if they miss those activities while they're with me. Our kids
    have told me their other parent calls me "selfish" and says I "don't really love
    them" when I ask to swap weekends. One of the kids has started getting stomach
    aches on transition days. I want to modify custody so they live primarily with
    me and to have clearer rules about scheduling decisions.
    """,
    # 6. New partner with concerning history - borderline on third-party involvement
    """
    Our current order gives me primary physical custody and gives my ex alternate
    weekends and one midweek visit. When the order was made, neither of us was in
    a serious relationship, so the judgment doesn't mention anything about new
    partners being around the kids.

    Now my ex lives with someone who has a criminal record for assault and battery
    and had a restraining order from a previous girlfriend. My kids have mentioned
    that this person yells a lot, slams doors, and once grabbed one of them hard
    enough to leave a mark on their arm. A neighbor called the police during a loud
    argument when the kids were there. I'm asking the court to change the order so
    that either this person isn't around during visits or the visits are supervised.
    """,
    # 7. Other parent's serious health decline - borderline on accommodation
    """
    The original court order gave us 50/50 physical custody, one week on and one
    week off, when we both lived nearby and were healthy. That worked well for
    several years—our daughter had good routines in both homes.

    Recently my co-parent was diagnosed with a progressive neurological condition.
    They've fallen several times at home, and their doctor has told them they
    shouldn't be alone with our child near stairs or in situations requiring quick
    physical response. But they still insist on keeping the exact same 50/50 schedule
    and sometimes rely on our twelve-year-old daughter to help them move from their
    wheelchair to bed or bring them things. I'm asking the court to adjust things so
    our daughter is primarily with me while my ex has time that fits what they can
    safely handle.
    """,
    # 8. Ex won't get kid to school - borderline on educational impact
    """
    The current judgment says we share legal custody, I'm the primary residential
    parent, and my ex has substantial weekend time, including Sunday nights. We're
    supposed to cooperate on school matters and keep each other informed. When the
    order was made, our child was doing fine in school.

    Over the past year, my ex has been keeping our child home from school on Mondays
    after their weekends together, saying she "needs a mental health day." There are
    no doctor notes for any of these absences. We've gotten truancy warnings from
    the school, and our daughter's grades and test scores have dropped. My ex also
    regularly refuses to take her to tutoring sessions that fall during his weekends.
    I want to change the order to give me final say on school attendance decisions
    or reduce his school-night overnights.
    """,
    # 9. Ex moved far away, wants same midweek overnight - distance + school conflict
    """
    Our order from 2019 gives me primary custody and gives my ex every other weekend
    plus one midweek overnight on Wednesdays. At the time, we lived in the same town
    and the midweek overnight was just a quick five-minute drive to school the next
    morning.

    My ex has since moved to Cape Cod—about ninety miles away—and still insists on
    keeping that same Wednesday overnight. He picks our daughter up from school,
    drives all the way down there, and then wakes her up around 4:30 AM to drive
    back for school Thursday morning. She's constantly exhausted, and her teacher
    says her participation has dropped noticeably on Thursdays. I'm asking the court
    to eliminate that midweek overnight and adjust the weekend schedule so she isn't
    doing these marathon drives on school nights.
    """,
    # 10. Child wants more time with other parent - borderline on weight of child's preference
    """
    When our daughter was four, the court gave primary residence to her dad and gave
    me limited weekend time and one weeknight dinner. That setup was based on my being
    in grad school at the time, living in a small studio apartment, and not having a
    flexible schedule. It was the best I could manage then.

    Now she's ten years old. I finished school, have a stable job with normal hours,
    and live in a two-bedroom apartment where she has her own room. She and I have
    gotten very close, and her therapist says she feels guilty having to leave after
    short visits and wants more time with me. She's actually written a letter to the
    judge saying she wants more overnights at my place. Her dad refuses to discuss
    any changes and gets angry when she brings it up. I'm asking the court to update
    the schedule so she can spend more time with me.
    """,
]
