import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class MenuItem:
    """Class untuk merepresentasikan item menu makanan atau minuman."""

    def __init__(self, nama: str, kategori: str, harga: float):
        self._nama = nama
        self._kategori = kategori
        self._harga = 0.0

        self.harga = harga

    @property
    def nama(self) -> str:
        """Getter untuk mendapatkan nama menu."""
        return self._nama

    @property
    def kategori(self) -> str:
        """Getter untuk mendapatkan kategori menu."""
        return self._kategori

    @property
    def harga(self) -> float:
        """Getter untuk mendapatkan harga menu."""
        return self._harga

    @harga.setter
    def harga(self, nilai: float):
        """Setter harga dengan validasi logika: harga harus angka positif > 0."""
        if not isinstance(nilai, (int, float)):
            raise TypeError("Harga menu harus berupa bilangan numerik!")
        if nilai <= 0:
            raise ValueError("Harga menu tidak valid! Harga harus lebih besar dari Rp 0.")
        self._harga = float(nilai)

    @classmethod
    def dari_dict(cls, data: dict):
        """
        Class Method: Factory method untuk membuat instance MenuItem dari dictionary data.
        Menerima parameter 'cls' yang merujuk pada class MenuItem itu sendiri.
        """
        return cls(
            nama=data.get("nama", "Tanpa Nama"),
            kategori=data.get("kategori", "Umum"),
            harga=data.get("harga", 0.0)
        )

    def get_info_tabel(self):
        """Mengembalikan data tuple yang siap ditampilkan pada tabel Treeview."""
        return (self._nama, self._kategori, Pesanan.format_rupiah(self._harga))

    def __str__(self):
        """Representasi string dari objek menu."""
        return f"{self._nama} ({self._kategori}) - {Pesanan.format_rupiah(self._harga)}"


class Pesanan:
    """Class untuk mengelola transaksi pemesanan makanan."""

    _counter_pesanan = 100

    def __init__(self, nomor_pesanan: str = None):
        self._nomor = nomor_pesanan if nomor_pesanan else Pesanan.nomor_berikutnya()
        self._waktu = datetime.now()
        self._items = []

    @property
    def nomor(self) -> str:
        """Getter untuk nomor pesanan."""
        return self._nomor

    @property
    def waktu(self) -> datetime:
        """Getter untuk waktu pemesanan."""
        return self._waktu

    @property
    def items(self) -> list:
        """Getter untuk daftar item dalam pesanan."""
        return self._items

    @property
    def total_harga(self) -> float:
        """Getter kalkulasi total harga dari seluruh subtotal item."""
        return sum(item["subtotal"] for item in self._items)

    @classmethod
    def nomor_berikutnya(cls) -> str:
        """
        Class Method: Menghasilkan kode pesanan otomatis berikutnya (auto-increment).
        Mengakses dan mengubah class attribute '_counter_pesanan'.
        """
        cls._counter_pesanan += 1
        return f"ORD-{cls._counter_pesanan:03d}"

    @staticmethod
    def format_rupiah(angka: float) -> str:
        """
        Static Method: Fungsi utilitas pembantu untuk format angka menjadi format 'Rp XX.XXX'.
        Tidak bergantung pada state instance (self) maupun class (cls).
        """
        try:
            nilai = int(round(float(angka)))
            return f"Rp {nilai:,.0f}".replace(",", ".")
        except (ValueError, TypeError):
            return "Rp 0"

    def tambah_item(self, menu: MenuItem, jumlah: int):
        """Menambahkan menu ke dalam pesanan atau memperbarui jumlah jika sudah ada."""
        if jumlah <= 0:
            raise ValueError("Jumlah pesanan harus minimal 1!")

        for item in self._items:
            if item["menu"].nama == menu.nama:
                item["jumlah"] += jumlah
                item["subtotal"] = item["menu"].harga * item["jumlah"]
                return

        subtotal = menu.harga * jumlah
        self._items.append({
            "menu": menu,
            "jumlah": jumlah,
            "subtotal": subtotal
        })

    def hapus_item(self, indeks: int):
        """Menghapus item pesanan berdasarkan indeks di keranjang."""
        if 0 <= indeks < len(self._items):
            return self._items.pop(indeks)
        return None

    def kosongkan(self):
        """Mengosongkan semua item dalam pesanan."""
        self._items.clear()

    def jumlah_item(self) -> int:
        """Mengembalikan total jenis item yang ada di keranjang."""
        return len(self._items)

    def cetak_struk_teks(self) -> str:
        """Menghasilkan teks struk pembelian yang terformat rapi."""
        garis = "=" * 46
        pemisah = "-" * 46
        waktu_str = self._waktu.strftime("%d/%m/%Y %H:%M:%S")

        teks = [
            garis,
            "ALTHAF RESTO".center(46),
            "Jl. Pakupatan, Samping Kampus UNIBA".center(46),
            garis,
            f"No. Pesanan : {self._nomor}",
            f"Waktu       : {waktu_str}",
            pemisah,
            f"{'Item':<20} {'Qty':<5} {'Subtotal':>18}",
            pemisah
        ]

        for item in self._items:
            nama_item = item["menu"].nama
            if len(nama_item) > 18:
                nama_item = nama_item[:15] + "..."
            qty = str(item["jumlah"])
            subtot = Pesanan.format_rupiah(item["subtotal"])
            teks.append(f"{nama_item:<20} {qty:<5} {subtot:>18}")

        teks.extend([
            pemisah,
            f"{'TOTAL PEMBAYARAN':<25} {Pesanan.format_rupiah(self.total_harga):>20}",
            garis,
            "     Terima kasih atas pesanan Anda!      ",
            "         Selamat menikmati hidangan!       ",
            garis
        ])
        return "\n".join(teks)


class AplikasiPemesanan:
    """Class GUI utama untuk Sistem Pemesanan Makanan menggunakan Tkinter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistem Pemesanan Makanan - OOP Tkinter")
        self.root.geometry("1020x680")
        self.root.minsize(920, 600)
        self.root.configure(bg="#F4F6F9")

        self.daftar_menu = []
        self._inisialisasi_menu_default()

        self.pesanan_aktif = Pesanan()

        self._konfigurasi_tema()

        self._buat_antarmuka()

    def _inisialisasi_menu_default(self):
        """
        Membuat objek MenuItem dari sekumpulan data dictionary
        menggunakan [SYARAT 8] Class Method MenuItem.dari_dict()
        dan [SYARAT 3] Membuat Object dari class.
        """
        data_mentah = [
            {"nama": "Nasi Goreng Spesial", "kategori": "Makanan", "harga": 25000},
            {"nama": "Ayam Bakar Madu", "kategori": "Makanan", "harga": 30000},
            {"nama": "Mie Goreng Seafood", "kategori": "Makanan", "harga": 28000},
            {"nama": "Sate Ayam Madura (10 tsk)", "kategori": "Makanan", "harga": 27000},
            {"nama": "Soto Betawi Daging", "kategori": "Makanan", "harga": 35000},
            {"nama": "Es Teh Manis", "kategori": "Minuman", "harga": 6000},
            {"nama": "Es Jeruk Peras", "kategori": "Minuman", "harga": 9000},
            {"nama": "Jus Alpukat Kocok", "kategori": "Minuman", "harga": 16000},
            {"nama": "Kopi Susu Gula Aren", "kategori": "Minuman", "harga": 18000},
            {"nama": "Kentang Goreng Crispy", "kategori": "Cemilan", "harga": 15000},
            {"nama": "Pisang Bakar Coklat Keju", "kategori": "Cemilan", "harga": 14000},
            {"nama": "Tahu Walik Krispi", "kategori": "Cemilan", "harga": 12000},
        ]

        for item in data_mentah:
            objek_menu = MenuItem.dari_dict(item)
            self.daftar_menu.append(objek_menu)

    def _konfigurasi_tema(self):
        """Konfigurasi gaya visual ttk untuk tampilan yang modern dan bersih."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        primary_color = "#1E3A8A"
        bg_card = "#FFFFFF"

        self.style.configure(".", font=("Segoe UI", 10), background="#F4F6F9")
        self.style.configure("Card.TFrame", background=bg_card, relief="flat")
        self.style.configure("Treeview",
                             font=("Segoe UI", 10),
                             rowheight=28,
                             background="#FFFFFF",
                             fieldbackground="#FFFFFF")
        self.style.configure("Treeview.Heading",
                             font=("Segoe UI", 10, "bold"),
                             background="#E2E8F0",
                             foreground="#1E293B",
                             padding=5)
        self.style.map("Treeview", background=[("selected", "#3B82F6")],
                       foreground=[("selected", "#FFFFFF")])

        self.style.configure("Primary.TButton",
                             font=("Segoe UI", 10, "bold"),
                             background=primary_color,
                             foreground="#FFFFFF",
                             padding=8)
        self.style.map("Primary.TButton",
                       background=[("active", "#2563EB"), ("disabled", "#94A3B8")])

        self.style.configure("Danger.TButton",
                             font=("Segoe UI", 9, "bold"),
                             background="#DC2626",
                             foreground="#FFFFFF",
                             padding=6)
        self.style.map("Danger.TButton",
                       background=[("active", "#B91C1C")])

        self.style.configure("Success.TButton",
                             font=("Segoe UI", 11, "bold"),
                             background="#059669",
                             foreground="#FFFFFF",
                             padding=10)
        self.style.map("Success.TButton",
                       background=[("active", "#047857"), ("disabled", "#A7F3D0")])

    def _buat_antarmuka(self):
        """Membangun layout antarmuka pengguna Tkinter."""
        header_frame = tk.Frame(self.root, bg="#1E3A8A", height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        lbl_judul = tk.Label(
            header_frame,
            text="🍽️ SISTEM PEMESANAN MAKANAN",
            font=("Segoe UI", 16, "bold"),
            bg="#1E3A8A",
            fg="#FFFFFF"
        )
        lbl_judul.pack(side=tk.LEFT, padx=25, pady=10)

        lbl_subjudul = tk.Label(
            header_frame,
            text="Tugas Pemrograman Berorientasi Objek (OOP)",
            font=("Segoe UI", 10, "italic"),
            bg="#1E3A8A",
            fg="#93C5FD"
        )
        lbl_subjudul.pack(side=tk.RIGHT, padx=25, pady=15)

        kontainer_utama = tk.Frame(self.root, bg="#F4F6F9")
        kontainer_utama.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        kontainer_utama.columnconfigure(0, weight=6)
        kontainer_utama.columnconfigure(1, weight=5)
        kontainer_utama.rowconfigure(0, weight=1)

        frame_kiri = tk.Frame(kontainer_utama, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        frame_kiri.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl_menu_title = tk.Label(
            frame_kiri,
            text="📋 Daftar Menu Restoran",
            font=("Segoe UI", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E293B"
        )
        lbl_menu_title.pack(anchor="w", padx=15, pady=(15, 5))

        filter_frame = tk.Frame(frame_kiri, bg="#FFFFFF")
        filter_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Label(filter_frame, text="Filter Kategori:", font=("Segoe UI", 9), bg="#FFFFFF", fg="#64748B").pack(side=tk.LEFT, padx=(0, 6))

        self.kategori_var = tk.StringVar(value="Semua")
        pilihan_kategori = ["Semua", "Makanan", "Minuman", "Cemilan"]
        for kat in pilihan_kategori:
            rb = tk.Radiobutton(
                filter_frame,
                text=kat,
                value=kat,
                variable=self.kategori_var,
                command=self._filter_tampilan_menu,
                bg="#FFFFFF",
                activebackground="#FFFFFF",
                font=("Segoe UI", 9)
            )
            rb.pack(side=tk.LEFT, padx=4)

        kolom_menu = ("nama", "kategori", "harga")
        self.tabel_menu = ttk.Treeview(
            frame_kiri,
            columns=kolom_menu,
            show="headings",
            selectmode="browse",
            height=12
        )
        self.tabel_menu.heading("nama", text="Nama Menu", anchor="w")
        self.tabel_menu.heading("kategori", text="Kategori", anchor="center")
        self.tabel_menu.heading("harga", text="Harga Satuan", anchor="e")

        self.tabel_menu.column("nama", width=220, anchor="w")
        self.tabel_menu.column("kategori", width=100, anchor="center")
        self.tabel_menu.column("harga", width=120, anchor="e")

        scroll_menu = ttk.Scrollbar(frame_kiri, orient=tk.VERTICAL, command=self.tabel_menu.yview)
        self.tabel_menu.configure(yscrollcommand=scroll_menu.set)

        self.tabel_menu.pack(fill=tk.BOTH, expand=True, padx=(15, 0), pady=(0, 10), side=tk.TOP)
        scroll_menu.place(in_=self.tabel_menu, relx=1.0, relheight=1.0, bordermode="outside")

        panel_tambah = tk.Frame(frame_kiri, bg="#F1F5F9", bd=1, relief=tk.GROOVE)
        panel_tambah.pack(fill=tk.X, padx=15, pady=(0, 15))

        lbl_qty = tk.Label(
            panel_tambah,
            text="Jumlah:",
            font=("Segoe UI", 10, "bold"),
            bg="#F1F5F9",
            fg="#1E293B"
        )
        lbl_qty.pack(side=tk.LEFT, padx=(15, 8), pady=12)

        self.spin_jumlah = ttk.Spinbox(
            panel_tambah,
            from_=1,
            to=99,
            width=5,
            font=("Segoe UI", 10),
            justify="center"
        )
        self.spin_jumlah.set(1)
        self.spin_jumlah.pack(side=tk.LEFT, padx=(0, 15), pady=12)

        btn_tambah = ttk.Button(
            panel_tambah,
            text="➕ Tambah ke Keranjang",
            style="Primary.TButton",
            command=self.aksi_tambah_ke_keranjang
        )
        btn_tambah.pack(side=tk.RIGHT, padx=15, pady=10)

        self._muat_tabel_menu()

        frame_kanan = tk.Frame(kontainer_utama, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        frame_kanan.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        header_keranjang = tk.Frame(frame_kanan, bg="#FFFFFF")
        header_keranjang.pack(fill=tk.X, padx=15, pady=(15, 10))

        lbl_cart_title = tk.Label(
            header_keranjang,
            text="🛒 Keranjang Pesanan",
            font=("Segoe UI", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E293B"
        )
        lbl_cart_title.pack(side=tk.LEFT)

        self.lbl_no_pesanan = tk.Label(
            header_keranjang,
            text=f"No: {self.pesanan_aktif.nomor}",
            font=("Segoe UI", 9, "bold"),
            bg="#E0E7FF",
            fg="#3730A3",
            padx=8,
            pady=3
        )
        self.lbl_no_pesanan.pack(side=tk.RIGHT)

        kolom_cart = ("nama", "jumlah", "subtotal")
        self.tabel_keranjang = ttk.Treeview(
            frame_kanan,
            columns=kolom_cart,
            show="headings",
            selectmode="browse",
            height=8
        )
        self.tabel_keranjang.heading("nama", text="Menu", anchor="w")
        self.tabel_keranjang.heading("jumlah", text="Qty", anchor="center")
        self.tabel_keranjang.heading("subtotal", text="Subtotal", anchor="e")

        self.tabel_keranjang.column("nama", width=170, anchor="w")
        self.tabel_keranjang.column("jumlah", width=50, anchor="center")
        self.tabel_keranjang.column("subtotal", width=110, anchor="e")

        scroll_cart = ttk.Scrollbar(frame_kanan, orient=tk.VERTICAL, command=self.tabel_keranjang.yview)
        self.tabel_keranjang.configure(yscrollcommand=scroll_cart.set)

        self.tabel_keranjang.pack(fill=tk.BOTH, expand=True, padx=(15, 0), pady=(0, 5), side=tk.TOP)
        scroll_cart.place(in_=self.tabel_keranjang, relx=1.0, relheight=1.0, bordermode="outside")

        frame_aksi_cart = tk.Frame(frame_kanan, bg="#FFFFFF")
        frame_aksi_cart.pack(fill=tk.X, padx=15, pady=(5, 10))

        btn_hapus = ttk.Button(
            frame_aksi_cart,
            text="🗑️ Hapus Item",
            style="Danger.TButton",
            command=self.aksi_hapus_item_keranjang
        )
        btn_hapus.pack(side=tk.LEFT)

        btn_reset = ttk.Button(
            frame_aksi_cart,
            text="Bersihkan Semua",
            command=self.aksi_reset_keranjang
        )
        btn_reset.pack(side=tk.RIGHT)

        frame_total = tk.Frame(frame_kanan, bg="#F8FAFC", bd=1, relief=tk.RIDGE)
        frame_total.pack(fill=tk.X, padx=15, pady=(0, 10))

        lbl_total_text = tk.Label(
            frame_total,
            text="Total Pembayaran:",
            font=("Segoe UI", 11),
            bg="#F8FAFC",
            fg="#475569"
        )
        lbl_total_text.pack(side=tk.LEFT, padx=15, pady=12)

        self.lbl_total_harga = tk.Label(
            frame_total,
            text="Rp 0",
            font=("Segoe UI", 14, "bold"),
            bg="#F8FAFC",
            fg="#059669"
        )
        self.lbl_total_harga.pack(side=tk.RIGHT, padx=15, pady=12)

        self.frame_proses = tk.Frame(frame_kanan, bg="#FFFFFF")
        self.frame_proses.pack(fill=tk.X, padx=15, pady=(0, 5))

        self.lbl_status_proses = tk.Label(
            self.frame_proses,
            text="",
            font=("Segoe UI", 9, "italic"),
            bg="#FFFFFF",
            fg="#64748B"
        )
        self.lbl_status_proses.pack(anchor="w", pady=(0, 2))

        self.progress_bar = ttk.Progressbar(
            self.frame_proses,
            orient="horizontal",
            mode="determinate",
            length=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar.pack_forget()

        self.btn_pesan = ttk.Button(
            frame_kanan,
            text="✅ Pesan Sekarang",
            style="Success.TButton",
            command=self.aksi_pesan_sekarang
        )
        self.btn_pesan.pack(fill=tk.X, padx=15, pady=(5, 15))

    def _muat_tabel_menu(self, kategori_filter: str = "Semua"):
        """Menampilkan menu pada Treeview berdasarkan filter yang dipilih."""
        for item in self.tabel_menu.get_children():
            self.tabel_menu.delete(item)

        for menu in self.daftar_menu:
            if kategori_filter == "Semua" or menu.kategori == kategori_filter:
                self.tabel_menu.insert("", tk.END, values=menu.get_info_tabel())

    def _filter_tampilan_menu(self):
        """Callback ketika radiobutton filter kategori diklik."""
        pilihan = self.kategori_var.get()
        self._muat_tabel_menu(pilihan)

    def _temukan_menu_by_nama(self, nama: str):
        """Mencari objek MenuItem berdasarkan nama menu."""
        for m in self.daftar_menu:
            if m.nama == nama:
                return m
        return None

    def aksi_tambah_ke_keranjang(self):
        """
        Handler saat tombol 'Tambah ke Keranjang' diklik.
        Menangani [FITUR] Validasi Input jika menu belum dipilih atau jumlah tidak valid.
        """
        seleksi = self.tabel_menu.selection()
        if not seleksi:
            messagebox.showwarning(
                "Peringatan",
                "Silakan pilih salah satu menu dari daftar terlebih dahulu!"
            )
            return

        item_terpilih = self.tabel_menu.item(seleksi[0])
        nama_menu = item_terpilih["values"][0]
        objek_menu = self._temukan_menu_by_nama(nama_menu)

        if not objek_menu:
            messagebox.showerror("Error", "Data menu tidak ditemukan!")
            return

        try:
            jumlah = int(self.spin_jumlah.get())
            if jumlah <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Kesalahan Input",
                "Jumlah pesanan harus berupa bilangan bulat positif (minimal 1)!"
            )
            self.spin_jumlah.set(1)
            return

        self.pesanan_aktif.tambah_item(objek_menu, jumlah)

        self._perbarui_tampilan_keranjang()
        self.spin_jumlah.set(1)

    def _perbarui_tampilan_keranjang(self):
        """Mengupdate tabel keranjang belanja dan label total harga."""
        for item in self.tabel_keranjang.get_children():
            self.tabel_keranjang.delete(item)

        for item_data in self.pesanan_aktif.items:
            nama = item_data["menu"].nama
            qty = item_data["jumlah"]
            subtot_str = Pesanan.format_rupiah(item_data["subtotal"])
            self.tabel_keranjang.insert("", tk.END, values=(nama, qty, subtot_str))

        total_str = Pesanan.format_rupiah(self.pesanan_aktif.total_harga)
        self.lbl_total_harga.config(text=total_str)

    def aksi_hapus_item_keranjang(self):
        """
        Handler untuk menghapus satu baris item dari keranjang pesanan.
        Menangani [FITUR] Validasi jika belum ada item keranjang yang dipilih.
        """
        seleksi = self.tabel_keranjang.selection()
        if not seleksi:
            messagebox.showwarning(
                "Peringatan",
                "Pilih item di tabel keranjang yang ingin Anda hapus!"
            )
            return

        indeks = self.tabel_keranjang.index(seleksi[0])
        self.pesanan_aktif.hapus_item(indeks)

        self._perbarui_tampilan_keranjang()

    def aksi_reset_keranjang(self):
        """Mengosongkan semua item dalam keranjang jika dikonfirmasi pengguna."""
        if self.pesanan_aktif.jumlah_item() == 0:
            return

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Reset",
            "Apakah Anda yakin ingin mengosongkan seluruh isi keranjang?"
        )
        if konfirmasi:
            self.pesanan_aktif.kosongkan()
            self._perbarui_tampilan_keranjang()

    def aksi_pesan_sekarang(self):
        """
        Handler saat tombol 'Pesan Sekarang' ditekan.
        Menangani [FITUR] Validasi keranjang kosong dan animasi progress bar using after().
        """
        if self.pesanan_aktif.jumlah_item() == 0:
            messagebox.showwarning(
                "Keranjang Kosong",
                "Keranjang belanja Anda masih kosong!\nSilakan pilih menu makanan terlebih dahulu."
            )
            return

        self.btn_pesan.config(state="disabled")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar["value"] = 0

        self._jalankan_animasi_progres(0)

    def _jalankan_animasi_progres(self, nilai: int):
        """
        Animasi progress bar halus tanpa freeze GUI menggunakan root.after().
        Mensimulasikan pemrosesan pesanan, pembayaran, hingga pembuatan struk.
        """
        if nilai <= 100:
            self.progress_bar["value"] = nilai

            if nilai < 30:
                self.lbl_status_proses.config(text="⏳ Memverifikasi pesanan...")
            elif nilai < 70:
                self.lbl_status_proses.config(text="💳 Memproses transaksi & pembayaran...")
            elif nilai < 95:
                self.lbl_status_proses.config(text="🧾 Menyiapkan struk pesanan...")
            else:
                self.lbl_status_proses.config(text="✨ Selesai!")

            self.root.after(25, lambda: self._jalankan_animasi_progres(nilai + 2))
        else:
            self.progress_bar.pack_forget()
            self.lbl_status_proses.config(text="")
            self.btn_pesan.config(state="normal")

            self._tampilkan_jendela_struk(self.pesanan_aktif)

            self.pesanan_aktif = Pesanan()
            self.lbl_no_pesanan.config(text=f"No: {self.pesanan_aktif.nomor}")

            self._perbarui_tampilan_keranjang()

    def _tampilkan_jendela_struk(self, pesanan_selesai: Pesanan):
        """Membuka jendela Toplevel khusus untuk menampilkan struk transaksi."""
        jendela_struk = tk.Toplevel(self.root)
        jendela_struk.title("Struk Transaksi Pesanan")
        jendela_struk.geometry("440x520")
        jendela_struk.resizable(False, False)
        jendela_struk.transient(self.root)
        jendela_struk.grab_set()
        jendela_struk.configure(bg="#F8FAFC")

        lbl_info = tk.Label(
            jendela_struk,
            text="✅ Pesanan Berhasil Diproses!",
            font=("Segoe UI", 12, "bold"),
            bg="#F8FAFC",
            fg="#059669"
        )
        lbl_info.pack(pady=(15, 5))

        teks_frame = tk.Frame(jendela_struk, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        teks_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        txt_struk = tk.Text(
            teks_frame,
            font=("Consolas", 10),
            bg="#FFFFF8",
            fg="#1E293B",
            wrap="none",
            bd=0,
            padx=10,
            pady=10
        )
        txt_struk.insert(tk.END, pesanan_selesai.cetak_struk_teks())
        txt_struk.config(state="disabled")
        txt_struk.pack(fill=tk.BOTH, expand=True)

        btn_tutup = ttk.Button(
            jendela_struk,
            text="Tutup & Buat Pesanan Baru",
            style="Primary.TButton",
            command=jendela_struk.destroy
        )
        btn_tutup.pack(pady=(0, 15))


if __name__ == "__main__":
    root = tk.Tk()

    app = AplikasiPemesanan(root)

    root.mainloop()

