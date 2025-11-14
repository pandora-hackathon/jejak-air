import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from profiles.models import UserProfile
from farms.models import City, Farm
from batches.models import HarvestBatch, Activity
from labs.models import Laboratory, LabTest

User = get_user_model()

def parse_int(value):
    value = (value or "").strip()
    return int(value) if value else None

def parse_float(value):
    value = (value or "").strip()
    return float(value) if value else None

def parse_bool(value):
    value = (value or "").strip().lower()
    return value in ("1", "true", "t", "yes", "y")

class Command(BaseCommand):
    help = "Import initial CSV data for aquaculture traceability app"

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            default="data",
            help="Folder berisi file CSV (default: ./data)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        base_dir = Path(options["data_dir"])
        self.stdout.write(self.style.NOTICE(f"Memakai folder data: {base_dir.resolve()}"))

        self.load_cities(base_dir)
        self.load_laboratories(base_dir)
        self.load_users(base_dir)
        self.load_user_profiles(base_dir)
        self.load_farms(base_dir)
        self.load_batches(base_dir)
        self.load_activities(base_dir)
        self.load_lab_tests(base_dir)

        self.stdout.write(self.style.SUCCESS("Import selesai tanpa error."))

    # === LOADERS ===

    def load_cities(self, base_dir: Path):
        path = base_dir / "cities.csv"
        self.stdout.write(f"Import City dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                city, created = City.objects.get_or_create(
                    name=row["name"].strip(),
                    defaults={
                        "province": row["province"].strip(),
                    },
                )
                if not created:
                    city.province = row["province"].strip()
                    city.save(update_fields=["province"])

    def load_laboratories(self, base_dir: Path):
        path = base_dir / "laboratories.csv"
        self.stdout.write(f"Import Laboratory dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                city = City.objects.get(name=row["city_name"].strip())
                lab, created = Laboratory.objects.get_or_create(
                    nama=row["nama"].strip(),
                    defaults={"city": city},
                )
                if not created and lab.city != city:
                    lab.city = city
                    lab.save(update_fields=["city"])

    def load_users(self, base_dir: Path):
        path = base_dir / "users.csv"
        self.stdout.write(f"Import User dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = row["username"].strip()
                email = row["email"].strip()
                role = row["role"].strip()
                first_name = row["first_name"].strip()
                last_name = row["last_name"].strip()
                password = row["password"].strip()

                # cek apakah user sudah ada
                try:
                    user = User.objects.get(username=username)
                    # update basic fields kalau mau
                    user.email = email
                    user.role = role
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save(update_fields=["email", "role", "first_name", "last_name"])
                except User.DoesNotExist:
                    # create_user akan otomatis hash password
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        role=role,
                        first_name=first_name,
                        last_name=last_name,
                    )

    def load_user_profiles(self, base_dir: Path):
        path = base_dir / "user_profiles.csv"
        self.stdout.write(f"Import UserProfile dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = row["username"].strip()
                phone = (row.get("number_phone") or "").strip()
                lab_name = (row.get("laboratory_name") or "").strip() or None

                user = User.objects.get(username=username)

                laboratory = None
                if lab_name:
                    laboratory = Laboratory.objects.get(nama=lab_name)

                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "number_phone": phone or None,
                        "laboratory": laboratory,
                    },
                )
                if not created:
                    profile.number_phone = phone or None
                    profile.laboratory = laboratory
                    profile.save()

    def load_farms(self, base_dir: Path):
        path = base_dir / "farms.csv"
        self.stdout.write(f"Import Farm dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                city = City.objects.get(name=row["city_name"].strip())
                farm, created = Farm.objects.get_or_create(
                    name=row["name"].strip(),
                    defaults={
                        "city": city,
                        "location": row["location"].strip(),
                        # risk_score pakai default=30 dulu
                    },
                )
                if not created:
                    farm.city = city
                    farm.location = row["location"].strip()
                    farm.save()

    def load_batches(self, base_dir: Path):
        path = base_dir / "batches.csv"
        self.stdout.write(f"Import HarvestBatch dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                farm = Farm.objects.get(name=row["farm_name"].strip())
                kode_batch = row["kode_batch"].strip()
                is_shipped = parse_bool(row["is_shipped"])

                batch, created = HarvestBatch.objects.get_or_create(
                    kode_batch=kode_batch,
                    defaults={
                        "farm": farm,
                        "commodity": row["commodity"].strip(),
                        "tanggal_tebar": row["tanggal_tebar"].strip() or None,
                        "tanggal_panen": row["tanggal_panen"].strip(),
                        "volume_kg": float(row["volume_kg"]),
                        "tujuan": row["tujuan"].strip(),
                        "quality_status": row["quality_status"].strip() or "PENDING",
                        # risk_score biarkan NULL (None)
                        "is_shipped": is_shipped,
                    },
                )
                if not created:
                    batch.farm = farm
                    batch.commodity = row["commodity"].strip()
                    batch.tanggal_tebar = row["tanggal_tebar"].strip() or None
                    batch.tanggal_panen = row["tanggal_panen"].strip()
                    batch.volume_kg = float(row["volume_kg"])
                    batch.tujuan = row["tujuan"].strip()
                    batch.quality_status = row["quality_status"].strip() or "PENDING"
                    batch.is_shipped = is_shipped
                    batch.save()

    def load_activities(self, base_dir: Path):
        path = base_dir / "activities.csv"
        self.stdout.write(f"Import Activity dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                batch = HarvestBatch.objects.get(kode_batch=row["batch_kode"].strip())
                Activity.objects.get_or_create(
                    batch=batch,
                    tanggal=row["tanggal"].strip(),
                    jenis=row["jenis"].strip(),
                    lokasi=row["lokasi"].strip(),
                    pelaku=row["pelaku"].strip(),
                    keterangan=(row.get("keterangan") or "").strip(),
                )

    def load_lab_tests(self, base_dir: Path):
        path = base_dir / "lab_tests.csv"
        self.stdout.write(f"Import LabTest dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                batch = HarvestBatch.objects.get(kode_batch=row["batch_kode"].strip())
                qc_username = row["qc_username"].strip()
                qc_profile = UserProfile.objects.get(user__username=qc_username)

                nilai_cs137 = parse_float(row["nilai_cs137"])
                batas_aman_cs137 = parse_float(row["batas_aman_cs137"])

                lab_test, created = LabTest.objects.get_or_create(
                    batch=batch,
                    defaults={
                        "qc": qc_profile,
                        "nilai_cs137": nilai_cs137,
                        "batas_aman_cs137": batas_aman_cs137,
                        "kesimpulan": row["kesimpulan"].strip(),
                        "tanggal_uji": row["tanggal_uji"].strip(),
                    },
                )
                if not created:
                    lab_test.qc = qc_profile
                    lab_test.nilai_cs137 = nilai_cs137
                    lab_test.batas_aman_cs137 = batas_aman_cs137
                    lab_test.kesimpulan = row["kesimpulan"].strip()
                    lab_test.tanggal_uji = row["tanggal_uji"].strip()
                    lab_test.save()
