from django.core.management.base import BaseCommand
from session.models import Session, Slide


class Command(BaseCommand):
    help = 'Seed the database with the Greenish waste management session slides'

    def handle(self, *args, **options):
        session, created = Session.objects.get_or_create(
            code='GRN01X',
            defaults={
                'title': 'Greenish Waste Management Awareness',
                'facilitator_name': 'Greenish Facilitator',
                'facilitator_password': 'greenish2024',
                'status': 'waiting',
            }
        )

        if not created:
            self.stdout.write(self.style.WARNING('Session GRN01X already exists. Skipping.'))
            return

        slides_data = [
            # Section 1: Welcome
            {
                'order': 0, 'slide_type': 'info', 'title': 'Welcome to Greenish! 🌿',
                'content': 'Today we explore waste management\nand what we can do about it.\n\nGet ready to learn, play, and commit!',
            },
            {
                'order': 1, 'slide_type': 'info', 'title': 'Meet & Greet',
                'content': 'Join the session on your phone!\n\nEnter the code: GRN01X\nChoose your name and avatar.\n\nLet\'s see who\'s here!',
            },

            # Section 2: What is Waste?
            {
                'order': 2, 'slide_type': 'info', 'title': 'What is Waste?',
                'content': 'Waste is anything we discard\nafter using it — or never use at all.\n\nBut what counts as waste?',
            },
            {
                'order': 3, 'slide_type': 'activity', 'title': 'What Can I Do With It?',
                'activity_type': 'match',
                'activity_config': {
                    'pairs': [
                        {'term': 'Material Recovery Facility', 'definition': 'Sorts and separates recyclable materials from solid waste'},
                        {'term': 'Biodegradation', 'definition': 'Decomposition of organic matter by microorganisms'},
                        {'term': 'Landfill', 'definition': 'A waste disposal site, the oldest form of waste disposal'},
                        {'term': 'Recycling', 'definition': 'Converting waste into new materials and objects'},
                        {'term': 'Leachate', 'definition': 'Toxic liquid produced when waste is buried in the ground'},
                    ]
                },
            },

            # Section 3: Types & Sources
            {
                'order': 4, 'slide_type': 'info', 'title': 'Types of Waste',
                'content': 'Organic · Plastic · Paper · Metal · Glass\nMedical · Construction · Hazardous · E-waste\n\nEach type needs different handling.',
            },
            {
                'order': 5, 'slide_type': 'info', 'title': 'Where Does Waste Come From?',
                'content': 'Households · Agriculture · Industry\nHospitals · Markets · Streets\n\n60% of Egypt\'s waste is organic!',
                'shocking_fact': True,
            },
            {
                'order': 6, 'slide_type': 'activity', 'title': 'Sort It Out!',
                'activity_type': 'sort',
                'activity_config': {
                    'items': ['Newspaper', 'Plastic Bottle', 'Banana Peel', 'Aluminum Can', 'Glass Jar', 'Medical Waste', 'Old Clothes', 'E-waste Phone'],
                    'bins': ['Reuse', 'Recycle', 'Dispose'],
                    'correct_bins': {
                        'Newspaper': 'Recycle',
                        'Plastic Bottle': 'Recycle',
                        'Banana Peel': 'Dispose',
                        'Aluminum Can': 'Recycle',
                        'Glass Jar': 'Reuse',
                        'Medical Waste': 'Dispose',
                        'Old Clothes': 'Reuse',
                        'E-waste Phone': 'Recycle',
                    }
                },
            },

            # Section 4: Why is Waste a Problem?
            {
                'order': 7, 'slide_type': 'info', 'title': 'Why Is Waste a Problem?',
                'content': 'Pollution · Health risks · Climate impact\nGroundwater contamination · Open burning\n\nWaste affects everyone.',
            },
            {
                'order': 8, 'slide_type': 'info',
                'title': '1,750 kg per household per day',
                'content': 'The average Egyptian household\nproduces 1.75 kg of waste daily.\n\nThat\'s 30,000 families × 1.75 kg\n= 52,500 kg EVERY DAY\nin a city of 150,000 people.',
                'shocking_fact': True,
            },
            {
                'order': 9, 'slide_type': 'activity', 'title': 'What Problems Do You See?',
                'activity_type': 'problem',
                'activity_config': {'prompt': 'Look at these images. What waste problems can you identify in your own community?'},
            },

            # Section 5: Biodegradable vs Non-biodegradable
            {
                'order': 10, 'slide_type': 'info', 'title': 'Biodegradable vs Non-biodegradable',
                'content': 'Biodegradable: Decomposes naturally\nPaper, food scraps, cotton, wood\n\nNon-biodegradable: Survives for centuries\nPlastic, glass, metal, aluminum\n\n60% of Egypt\'s waste IS biodegradable.',
            },
            {
                'order': 11, 'slide_type': 'activity', 'title': 'Is It Biodegradable?',
                'activity_type': 'poll',
                'activity_config': {
                    'question': 'Which of these takes the LONGEST to decompose?',
                    'options': ['Cotton cloth (1-5 months)', 'Wood (10-15 years)', 'Aluminum can (100-500 years)', 'Plastic bag (1 million years)'],
                    'correct': 3,
                },
            },

            # Section 6: How Long Does It Stay?
            {
                'order': 12, 'slide_type': 'info',
                'title': 'How Long Will It Stay With Us?',
                'content': 'Not all waste disappears at the same rate.\n\nSome things you threw away as a child\nare STILL in a landfill today.\n\nLet\'s see how long things really last...',
            },
            {
                'order': 13, 'slide_type': 'info',
                'title': 'A plastic bag lives longer than you.',
                'content': 'Orange peel: 2-5 weeks\nPaper: 2-4 weeks\nCotton cloth: 1-5 months\nWool: 1 year\nWood: 10-15 years\nAluminum can: 100-500 years\nPlastic bag: 1 million years\nGlass bottle: 1 million years\n\nThat plastic bag your grandmother used?\nIt\'s still there.',
                'shocking_fact': True,
            },
            {
                'order': 14, 'slide_type': 'activity', 'title': 'How Long Will It Stay?',
                'activity_type': 'guess',
                'activity_config': {
                    'question': 'How long does it take for an ALUMINUM CAN to decompose?',
                    'item': 'Aluminum Can 🥫',
                    'options': ['10-15 years', '50-100 years', '100-500 years', '1 million years'],
                    'correct': '100-500 years',
                },
            },

            # Section 7: What Can We Do?
            {
                'order': 15, 'slide_type': 'info', 'title': 'What Can We Do With Waste?',
                'content': 'The waste hierarchy:\n\n♻️ Reduce → Reuse → Recycle → Recover → Dispose\n\nStart at the top. Prevent first.\nRecycle when you can\'t prevent.\nDispose only as a last resort.',
            },
            {
                'order': 16, 'slide_type': 'info', 'title': 'Innovation Examples',
                'content': 'Banlastic — Plastic → new products, awareness events\n\nBekia — Sort waste, earn points, get rewards\n\nBiodiesel Misr — Used cooking oil → clean fuel\n\nBiogas — Organic waste → energy\n\nComposting — 60% of Egypt\'s waste → fertilizer',
            },
            {
                'order': 17, 'slide_type': 'activity', 'title': '♻️ Recycling & Reuse Race!',
                'activity_type': 'sort',
                'activity_config': {
                    'items': ['Tires', 'Glass Bottles', 'Egg Cartons', 'Medicine Bottles', 'Old T-shirts', 'Plastic Bags', 'Styrofoam', 'Food Scraps'],
                    'bins': ['Reuse', 'Recycle', 'Dispose'],
                    'correct_bins': {
                        'Tires': 'Reuse',
                        'Glass Bottles': 'Recycle',
                        'Egg Cartons': 'Recycle',
                        'Medicine Bottles': 'Dispose',
                        'Old T-shirts': 'Reuse',
                        'Plastic Bags': 'Recycle',
                        'Styrofoam': 'Dispose',
                        'Food Scraps': 'Dispose',
                    }
                },
            },

            # Section 8: Real-Life Challenges
            {
                'order': 18, 'slide_type': 'info', 'title': 'Real-Life Challenges',
                'content': 'Dahshur case study:\n\n• 60% organic waste, no collection system\n• Only 2 collection points for 50,000 people\n• Waste dumped in canals or burned\n• Nearest disposal site: 120 km away\n• Women lack job opportunities\n\nBut residents WILL pay for better services.',
            },
            {
                'order': 19, 'slide_type': 'activity', 'title': 'Community Problem Wall',
                'activity_type': 'discuss',
                'activity_config': {
                    'prompt': 'What waste challenges does YOUR community face? Share anonymously.',
                    'max_chars': 280,
                },
            },
            {
                'order': 20, 'slide_type': 'activity', 'title': 'Transfer Station Design',
                'activity_type': 'case_study',
                'activity_config': {
                    'description': 'A small village produces 200 kg of waste per day (50% organic). Nearest disposal site is 120 km away. The village needs fertilizer for agriculture.\n\nShould they build a transfer station? What would you include?',
                    'questions': [
                        'How would you collect waste from households?',
                        'What would you do with the organic waste?',
                        'Where would you locate any facilities?',
                        'How would you fund this system?',
                    ]
                },
            },

            # Section 9: What Can YOU Do?
            {
                'order': 21, 'slide_type': 'info', 'title': 'What Can YOU Do?',
                'content': 'Individual actions:\n• Reduce — buy less, buy in bulk\n• Reuse — returnable bottles, repair old things\n• Recycle — sort your waste\n• Compost — turn organic waste into soil\n\nCommunity actions:\n• Organize cleanups\n• Advocate for better services\n• Support local recycling initiatives',
            },
            {
                'order': 22, 'slide_type': 'activity', 'title': '💚 My Commitment',
                'activity_type': 'commit',
                'activity_config': {
                    'prompt': 'I will...',
                },
            },

            # Section 10: Closing
            {
                'order': 23, 'slide_type': 'info', 'title': 'Thank You! 🌿',
                'content': 'The butterfly effect never ends.\nThe butterfly effect never fades.\n\nEvery action matters.\nEvery choice counts.\n\nLet\'s create a green world,\ngenerous and sincere as your heart.\n\n— In memory of Medhat Mohamed Mohamed Benzhair',
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

        self.stdout.write(self.style.SUCCESS(f'Created session GRN01X with {len(slides_data)} slides'))
        self.stdout.write(self.style.SUCCESS(f'Facilitator password: greenish2024'))
        self.stdout.write(self.style.SUCCESS(f'Join URL: /session/GRN01X/join/'))
        self.stdout.write(self.style.SUCCESS(f'Facilitator URL: /session/GRN01X/facilitator/'))