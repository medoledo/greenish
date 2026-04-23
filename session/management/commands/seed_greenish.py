from django.core.management.base import BaseCommand
from session.models import Session, Slide


class Command(BaseCommand):
    help = 'Seed the database with a complete Greenish waste management session'

    def handle(self, *args, **options):
        session = Session.objects.create(
            title='Greenish Club — Dahshur',
            facilitator_name='Greenish Facilitator',
            facilitator_password='greenish2024',
            status='waiting',
        )
        self.stdout.write(self.style.SUCCESS(f'Created session: {session.code}'))

        slides_data = [

            # TOPIC 0: WELCOME (2 slides)
            {
                'order': 0, 'slide_type': 'info', 'title': 'Welcome to Greenish Club! 🌿',
                'content': 'Today we explore waste management\nand discover what we can do about it.\n\nGet ready to learn, play, and make a difference!',
            },
            {
                'order': 1, 'slide_type': 'info', 'title': 'Join on Your Phone! 📱',
                'content': 'Open your browser and go to:\n\n  /session/' + session.code + '/join/\n\nEnter your name, pick an avatar,\nand let\'s see who\'s in the room!',
            },

            # TOPIC 1: WHAT IS WASTE? (2 slides + sprint activity)
            {
                'order': 2, 'slide_type': 'info', 'title': 'What is Waste?',
                'content': 'Waste is anything we discard\nafter using it — or never used at all.\n\nThe food you don\'t finish,\nthe bag you carry once,\nthe bottle you toss away.\n\nAll of it counts.',
            },
            {
                'order': 3, 'slide_type': 'activity', 'title': '♻️ Waste Sorting Sprint!',
                'activity_type': 'sprint',
                'activity_config': {'template': 'sprint'},
            },

            # TOPIC 2: TYPES & SOURCES (3 slides)
            {
                'order': 4, 'slide_type': 'info', 'title': 'Types of Waste',
                'content': 'Organic — food scraps, garden waste\nPlastic — bags, bottles, packaging\nPaper — newspapers, cartons, cardboard\nMetal — cans, foil, old utensils\nGlass — bottles, jars\nMedical — expired medicine, syringes\nConstruction — bricks, rubble, timber\nE-waste — phones, cables, batteries\n\nEach type needs different handling.',
            },
            {
                'order': 5, 'slide_type': 'info', 'title': 'Where Does It Come From?',
                'content': 'Our homes · Our markets\nOur farms · Our factories\nOur hospitals · Our streets',
                'shocking_fact': True,
            },
            {
                'order': 6, 'slide_type': 'info', 'title': 'The Egypt Reality 🇪🇬',
                'content': '26 million tons of waste per year\n50% is food and organic waste\nOnly 12% is recycled\n\nEgypt is among the highest\nwaste-generating countries\nin the Middle East.',
                'shocking_fact': True,
            },
            {
                'order': 7, 'slide_type': 'activity', 'title': '💬 What Waste Do You See?',
                'activity_type': 'discuss',
                'activity_config': {
                    'template': 'discuss',
                    'prompt': 'Share one type of waste you see every day in your community.',
                    'max_chars': 280,
                },
            },

            # TOPIC 3: WHY IS IT A PROBLEM? (2 slides + sort_stats activity)
            {
                'order': 8, 'slide_type': 'info', 'title': 'Why Is Waste a Problem?',
                'content': '💨 Open burning releases toxic gases\ninto the air we breathe.\n\n💧 Landfills contaminate groundwater\nthat communities depend on.\n\n🦠 Uncollected waste breeds disease\nand attracts pests.\n\n🌡️ Methane from waste is 80x more\npotent than CO₂ as a greenhouse gas.',
            },
            {
                'order': 9, 'slide_type': 'info', 'title': 'The Numbers Are Alarming 😰',
                'content': '100 million marine animals\nkilled by plastic pollution each year.\n\nOnly 9% of all plastic\never made has been recycled.\n\n1 million seabirds die\nfrom plastic entanglement annually.',
                'shocking_fact': True,
            },
            {
                'order': 10, 'slide_type': 'activity', 'title': '📊 True or False: Egypt Facts',
                'activity_type': 'sort_stats',
                'activity_config': {'template': 'sort_stats'},
            },

            # TOPIC 4: BIODEGRADABLE VS NON-BIODEGRADABLE (2 slides + decompose activity)
            {
                'order': 11, 'slide_type': 'info', 'title': 'Biodegradable vs Non-biodegradable',
                'content': '🌱 BIODEGRADABLE\nDecomposes naturally through\nbacteria, fungi, and weather.\n\nExamples:\nFood scraps, paper, cotton, wood, leaves\n\n⏳ NON-BIODEGRADABLE\nDoes not decompose — or takes centuries.\n\nExamples:\nPlastic, glass, metal, aluminum, rubber',
            },
            {
                'order': 12, 'slide_type': 'info', 'title': 'The Decomposition Gap 📊',
                'content': 'Food scraps: 2-5 weeks\nNewspaper: 6 weeks\nWool sock: 1 year\nPlastic bag: 500 years\nGlass bottle: 1 million years\n\nThe same material,\nthe same bin,\ndifferent lifetimes.',
                'shocking_fact': True,
            },
            {
                'order': 13, 'slide_type': 'activity', 'title': '⏳ Decomposition Race!',
                'activity_type': 'decompose',
                'activity_config': {'template': 'decompose'},
            },

            # TOPIC 5: HOW LONG DOES IT STAY? (2 slides + quiz activity)
            {
                'order': 14, 'slide_type': 'info', 'title': 'How Long Will It Stay With Us?',
                'content': 'Not all waste disappears at the same rate.\n\nSome things you threw away\nare STILL in a landfill today.\n\nLet\'s see how long\nthings really last...',
            },
            {
                'order': 15, 'slide_type': 'info', 'title': 'The Plastic Century 🛍️',
                'content': '1950 — Plastic production begins\nat industrial scale.\n\n2024 — 9 billion tons made.\n66 million tons per year.\n\nMost of it still exists.\n\nA plastic bag used in 1950?\nStill in a landfill somewhere.',
                'shocking_fact': True,
            },
            {
                'order': 16, 'slide_type': 'activity', 'title': '🌍 Plastic vs Planet Quiz!',
                'activity_type': 'quiz',
                'activity_config': {'template': 'quiz'},
            },

            # TOPIC 6: WHAT CAN WE DO? (3 slides + commitment activity)
            {
                'order': 17, 'slide_type': 'info', 'title': 'The Waste Hierarchy ♻️',
                'content': 'PREVENT — don\'t create it\nREDUCE — use less\nREUSE — use again\nRECYCLE — turn it into new\nRECOVER — extract energy\nDISPOSE — only as last resort\n\nStart at the top.\nEvery step up the pyramid\nmeans less waste in our world.',
            },
            {
                'order': 18, 'slide_type': 'info', 'title': 'Innovation in Egypt 🇪🇬',
                'content': '🏭 Banlastic\nTransforms plastic waste into\nnew products and wages awareness.\n\n🔄 Bekia\nRewards people for sorting waste.\nThey earn points, you earn clean streets.\n\n⛽ Biodiesel Misr\nTurns used cooking oil into clean fuel.\n\n🌱 Composting\n60% of Egypt\'s organic waste\nbecomes nutrient-rich fertilizer.',
            },
            {
                'order': 19, 'slide_type': 'activity', 'title': '💚 My Green Commitment!',
                'activity_type': 'commitment',
                'activity_config': {'template': 'commitment'},
            },

            # TOPIC 7: REAL-LIFE CHALLENGES & COMMUNITY (3 slides + discuss activity)
            {
                'order': 20, 'slide_type': 'info', 'title': 'The Dahshur Case Study 🏘️',
                'content': 'A village near Dahshur faces\nreal waste management challenges:\n\n• 60% of waste is organic\n• Only 2 collection points for 50,000 people\n• Nearest disposal site is 120 km away\n• Waste dumped in canals or burned openly\n• Women lack income opportunities\n\nBut residents say:\n"We WILL pay for better services."',
                'shocking_fact': True,
            },
            {
                'order': 21, 'slide_type': 'info', 'title': 'Community Role 🤝',
                'content': 'Waste management is not just\nthe government\'s job.\n\nIt starts with us:\n\n🌿 Organized cleanups\n🌿 Segregating at home\n🌿 Supporting local recyclers\n🌿 Reporting illegal dumping\n🌿 Teaching children\n\nSmall actions, big collective impact.',
            },
            {
                'order': 22, 'slide_type': 'activity', 'title': '💬 Community Discussion',
                'activity_type': 'discuss',
                'activity_config': {
                    'prompt': 'What waste challenges does YOUR community face? Share anonymously.',
                    'max_chars': 280,
                },
            },

            # TOPIC 8: WHAT CAN YOU DO? (2 slides + commitment activity)
            {
                'order': 23, 'slide_type': 'info', 'title': 'Your Action Plan ✨',
                'content': 'AT HOME:\n🌿 Say no to single-use plastic bags\n🌿 Compost your food scraps\n🌿 Repair instead of replacing\n🌿 Buy in bulk, choose glass over plastic\n\nIN YOUR COMMUNITY:\n🌿 Join or organize cleanups\n🌿 Support local recycling initiatives\n🌿 Talk about waste with friends\n🌿 Report illegal dumping',
            },
            {
                'order': 24, 'slide_type': 'activity', 'title': '💚 My Personal Pledge!',
                'activity_type': 'commitment',
                'activity_config': {'template': 'commitment'},
            },

            # CLOSING (2 slides)
            {
                'order': 25, 'slide_type': 'info', 'title': 'Every Action Matters 🦋',
                'content': 'The butterfly effect never ends.\nThe butterfly effect never fades.\n\nOne less plastic bag today.\nOne more conversation this week.\nOne commitment kept over a month.\n\nIt all adds up.\n\nThe world doesn\'t change in a day.\nBut it changes one person at a time.',
            },
            {
                'order': 26, 'slide_type': 'info', 'title': 'Thank You! 🌿',
                'content': 'Thank you for being here.\nThank you for caring.\nThank you for learning.\n\nLet\'s create a green world,\ngenerous and sincere\nas your heart.\n\n— In memory of Medhat Mohamed Mohamed Benzhair',
            },
        ]

        for slide_data in slides_data:
            shocking = slide_data.pop('shocking_fact', False)
            slide = Slide(
                session=session,
                shocking_fact=shocking,
                is_active=True,
                **slide_data
            )
            slide.save()

        self.stdout.write(self.style.SUCCESS(f'Session created: {session.code}'))
        self.stdout.write(self.style.SUCCESS(f'Title: {session.title}'))
        self.stdout.write(self.style.SUCCESS(f'Slides created: {len(slides_data)}'))
        self.stdout.write(self.style.SUCCESS(f'Activities: 7 (sprint, discuss, sort_stats, decompose, quiz, commitment ×2, discuss)'))
        self.stdout.write(self.style.SUCCESS(f'Facilitator password: greenish2024'))
        self.stdout.write(self.style.SUCCESS(f'Join URL: /session/{session.code}/join/'))
        self.stdout.write(self.style.SUCCESS(f'Facilitator URL: /session/{session.code}/facilitator/'))
        self.stdout.write(self.style.SUCCESS(f'CMS URL: /session/cms/'))