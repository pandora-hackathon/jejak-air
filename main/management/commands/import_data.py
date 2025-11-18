import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.dateparse import parse_date

from profiles.models import UserProfile
from farms.models import City, Farm
from batches.models import HarvestBatch, Activity, Commodity
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
        self.load_commodities(base_dir)
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
                code = row["code"].strip()
                name = row["name"].strip()
                province = row["province"].strip()

                city, created = City.objects.update_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "province": province,
                    },
                )
                # if not created:
                #     city.province = row["province"].strip()
                #     city.save(update_fields=["province"])

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

    def load_commodities(self, base_dir: Path):
        path = base_dir / "commodities.csv"
        self.stdout.write(f"Import Commodity dari {path} ...")

        if not path.exists():
            self.stdout.write(self.style.WARNING("  → File commodities.csv tidak ditemukan, lewati."))
            return

        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["code"].strip()
                name = row["name"].strip()
                batas = parse_float(row.get("default_batas_aman_cs137"))

                commodity, created = Commodity.objects.update_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "default_batas_aman_cs137": batas,
                    },
                )


    def load_farms(self, base_dir: Path):
        path = base_dir / "farms.csv"
        self.stdout.write(f"Import Farm dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                city = City.objects.get(name=row["city_name"].strip())

                owner_username = row["owner_username"].strip()
                from profiles.models import UserProfile
                owner = UserProfile.objects.get(user__username=owner_username)

                farm, created = Farm.objects.get_or_create(
                    name=row["name"].strip(),
                    defaults={
                        "city": city,
                        "location": row["location"].strip(),
                        "owner": owner,
                        # risk_score pakai default=30 dulu
                    },
                )
                if not created:
                    farm.city = city
                    farm.location = row["location"].strip()
                    farm.owner = owner
                    farm.save()

    def load_batches(self, base_dir: Path):
        path = base_dir / "batches.csv"
        self.stdout.write(f"Import HarvestBatch dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                farm = Farm.objects.get(name=row["farm_name"].strip())
                is_shipped = parse_bool(row["is_shipped"])

                # kolom 'commodity' di CSV berisi kode, misal 'UDANG', 'BANDENG'
                commodity_code = row["commodity"].strip()
                commodity = Commodity.objects.get(code=commodity_code)

                tanggal_tebar_raw = (row.get("tanggal_tebar") or "").strip()
                tanggal_panen_raw = row["tanggal_panen"].strip()

                tanggal_tebar = parse_date(tanggal_tebar_raw) if tanggal_tebar_raw else None
                tanggal_panen = parse_date(tanggal_panen_raw)

                # TIDAK mengisi kode_batch → akan di-generate otomatis di HarvestBatch.save()
                batch = HarvestBatch(
                    farm=farm,
                    commodity=commodity,
                    tanggal_tebar=tanggal_tebar,
                    tanggal_panen=tanggal_panen,
                    volume_kg=float(row["volume_kg"]),
                    tujuan=row["tujuan"].strip(),
                    is_shipped=is_shipped,
                    # risk_score biarkan None, nanti dihitung setelah LabTest
                )
                batch.save()

    def load_activities(self, base_dir: Path):
        path = base_dir / "activities.csv"
        self.stdout.write(f"Import Activity (LAINNYA) dari {path} ...")
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                jenis = row["jenis"].strip()
                if jenis != "LAINNYA":
                    # Abaikan jenis lain, supaya tidak bentrok
                    # dengan event otomatis
                    continue

                batch = HarvestBatch.objects.get(kode_batch=row["batch_kode"].strip())
                Activity.objects.get_or_create(
                    batch=batch,
                    tanggal=row["tanggal"].strip(),
                    jenis="LAINNYA",
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

                lab_test, created = LabTest.objects.update_or_create(
                    batch=batch,
                    defaults={
                        "qc": qc_profile,
                        "nilai_cs137": nilai_cs137,
                        "tanggal_uji": row["tanggal_uji"].strip(),
                    },
                )

