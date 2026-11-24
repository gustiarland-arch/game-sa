package com.arlandsofia.olu.logic.romance;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;

/**
 * v4.5 systems running inside the v4.6 native game. Pure Java: stable offline
 * dates, choices, trust, gifts and promises without touching the main story ending.
 * The game world owns the day counter. This engine NEVER advances world time.
 */
public final class RomanceEngineV45 {
    public static final int SCHEMA = 2;
    public static final String CANON_ENDING_ID = "shared_canon_ending";
    private static final int MAX_LOG = 48;

    public static final class Scene {
        public final String id, title, location, description;
        public final int minimumTrust;
        private Scene(String id, String title, String location, String description, int trust) {
            this.id=id; this.title=title; this.location=location;
            this.description=description; this.minimumTrust=trust;
        }
    }
    public static final class Choice {
        public final String id, label, response;
        public final int trustChange, affectionChange;
        private Choice(String id,String label,String response,int trust,int affection) {
            this.id=id;this.label=label;this.response=response;
            this.trustChange=trust;this.affectionChange=affection;
        }
    }
    public static final class Gift {
        public final String id, name;
        public final int tokenCost, minTrust, minDates, trustChange, affectionChange;
        private Gift(String id,String name,int cost,int trust,int dates,int dt,int da) {
            this.id=id;this.name=name;this.tokenCost=cost;this.minTrust=trust;
            this.minDates=dates;this.trustChange=dt;this.affectionChange=da;
        }
    }
    public static final class Moment {
        public final String id,title,description,route;
        public final int minTrust,minDates;
        private Moment(String id,String title,String desc,String route,int trust,int dates) {
            this.id=id;this.title=title;this.description=desc;this.route=route;
            this.minTrust=trust;this.minDates=dates;
        }
    }
    public static final class PromiseRecord {
        public String id="";
        public int dueDay=1, baseDates=0, baseCare=0, baseGifts=0;
        public String status="PENDING";
        public PromiseRecord() {}
        private PromiseRecord(String id,int day) {this.id=id;this.dueDay=day;}
    }
    /** Public fields are required for com.badlogic.gdx.utils.Json persistence. */
    public static final class Snapshot {
        public int schema=SCHEMA;
        public String route="arland";
        public int day=1,trust=60,affection=50,tokens=3,datesCompleted=0,careActions=0;
        public int lastDateDay=0,lastDialogueDay=0;
        public String activeDate="",lastDate="",lastDateChoice="";
        public ArrayList<String> giftsGiven=new ArrayList<>();
        public ArrayList<PromiseRecord> promises=new ArrayList<>();
        public ArrayList<String> journal=new ArrayList<>();
        public ArrayList<String> dateHistory=new ArrayList<>();
        public ArrayList<String> resolvedMoments=new ArrayList<>();
        public Snapshot() {}
    }
    public static final class Result {
        public final boolean ok;
        public final String text;
        private Result(boolean ok,String text){this.ok=ok;this.text=text;}
    }

    private static final Scene[] SCENES = {
        new Scene("library","Catatan di Perpustakaan","perpustakaan","Mencari pesan kecil di sela buku.",0),
        new Scene("flower","Bunga Pilihan Kita","toko_bunga","Memilih satu bunga sebagai kenangan.",0),
        new Scene("arcade","Dua Pemain Satu Tim","arcade","Mencoba permainan bersama.",40),
        new Scene("city","Jalan Sore","jalan_kota","Menikmati langit sore bersama.",45),
        new Scene("dinner","Makan Malam Sederhana","kafe","Berbincang tanpa terburu-buru.",55),
        new Scene("stars","Janji di Bawah Langit","bukit_bintang","Memandang bintang berdua.",70)
    };
    private static final Gift[] GIFTS = {
        new Gift("flower","Bunga dengan Surat",2,0,0,2,6),
        new Gift("photo","Foto Polaroid",3,45,1,3,7),
        new Gift("bracelet","Gelang Kenangan",4,60,2,4,9),
        new Gift("musicbox","Kotak Musik",6,75,3,6,12)
    };
    private static final Moment[] MOMENTS = {
        new Moment("arland_letter","Surat Kecil Arland","Arland menunjukkan pesan tulus untuk Sofia.","arland",55,1),
        new Moment("sofia_sketch","Sketsa Rahasia Sofia","Sofia memperlihatkan sketsa untuk Arland.","sofia",55,1),
        new Moment("rain_together","Berteduh Berdua","Hujan mendadak datang dalam perjalanan.","both",60,2),
        new Moment("future_plan","Mimpi yang Sama","Membicarakan rencana yang ingin diwujudkan.","both",70,3)
    };
    private static final LinkedHashMap<String,String> PROMISES=new LinkedHashMap<>();
    static {
        PROMISES.put("on_time","Datang tepat waktu");
        PROMISES.put("listen","Mendengarkan pasangan");
        PROMISES.put("remember","Mengingat momen bersama");
    }

    private final String route;
    private final Snapshot state;
    public RomanceEngineV45(String route){this(route,null);}
    public RomanceEngineV45(String route,Snapshot saved){
        if(!"arland".equals(route)&&!"sofia".equals(route))throw new IllegalArgumentException("Route tidak valid");
        this.route=route;
        state=saved!=null&&route.equals(saved.route)?sanitize(saved):new Snapshot();
        state.route=route;
    }
    public String route(){return route;}
    public String partner(){return "arland".equals(route)?"Sofia":"Arland";}
    public int day(){return state.day;}
    public int trust(){return state.trust;}
    public int affection(){return state.affection;}
    public int tokens(){return state.tokens;}
    public int datesCompleted(){return state.datesCompleted;}
    public String activeDateId(){return state.activeDate;}
    public String canonEndingId(){return CANON_ENDING_ID;}
    public Snapshot snapshot(){return sanitize(state);}
    public List<String> journalEntries(){return new ArrayList<>(state.journal);}
    public List<String> dateHistory(){return new ArrayList<>(state.dateHistory);}
    public List<PromiseRecord> promises(){return sanitize(state).promises;}
    public List<Gift> gifts(){ArrayList<Gift> a=new ArrayList<>();Collections.addAll(a,GIFTS);return a;}
    public LinkedHashMap<String,String> promiseCatalog(){return new LinkedHashMap<>(PROMISES);}

    /** Only the original gameplay clock may advance time; prevents unlimited reward farming. */
    public Result syncWorldDay(int worldDay){
        if(worldDay<1 || worldDay>9999)return no("Hari dunia tidak valid.");
        if(worldDay==state.day)return yes("Hari telah sinkron.");
        if(worldDay<state.day) {
            // Preserve the forward-only romance clock. Older/rolled-back main saves
            // must not allow the same date/dialogue/reward to run a second time.
            // The save remains readable; the host can inform the player.
            return no("Save utama berasal dari hari yang lebih lama. Hari romance tidak dimundurkan.");
        }
        state.day=worldDay;
        int broken=0;
        for(PromiseRecord p:state.promises){
            if("PENDING".equals(p.status)&&state.day>p.dueDay){
                p.status="BROKEN";state.trust=clamp(state.trust-9);broken++;
                log("Hari "+state.day+": janji "+p.id+" tidak terpenuhi");
            }
        }
        return yes(broken>0?broken+" janji melewati tenggat.":"Hari romance mengikuti dunia.");
    }
    public Scene scene(String id){for(Scene s:SCENES)if(s.id.equals(id))return s;return null;}
    public List<Scene> availableDates(){
        if(!state.activeDate.isEmpty()||state.lastDateDay>=state.day)return Collections.emptyList();
        ArrayList<Scene> a=new ArrayList<>();
        for(Scene s:SCENES)if(state.trust>=s.minimumTrust)a.add(s);
        a.sort((x,y)->Integer.compare(Math.floorMod(x.id.hashCode()+state.day*31+route.hashCode(),97),
            Math.floorMod(y.id.hashCode()+state.day*31+route.hashCode(),97)));
        return a;
    }
    public Result startDate(String id){
        if(!state.activeDate.isEmpty())return no("Selesaikan kencan aktif dahulu.");
        if(state.lastDateDay>=state.day)return no("Kencan hari ini sudah dimainkan.");
        Scene scene=scene(id);
        if(scene==null||state.trust<scene.minimumTrust)return no("Lokasi belum dapat dipilih.");
        state.activeDate=id;
        log("Hari "+state.day+": kencan dimulai di "+scene.location);
        return yes(scene.title+" - "+scene.description);
    }
    public List<Choice> dateChoices(){
        if(state.activeDate.isEmpty())return Collections.emptyList();
        ArrayList<Choice> a=new ArrayList<>();
        String response="arland".equals(route)?"Arland menaruh perhatian pada Sofia.":"Sofia berbagi perasaannya pada Arland.";
        a.add(new Choice("listen","Dengarkan dengan tulus",response+" Kalian saling memahami.",5,4));
        a.add(new Choice("plan","Buat rencana berikutnya","Kalian memilih tempat lain untuk dikenang.",2,7));
        a.add(new Choice("rush","Akhiri terlalu cepat","Ada yang belum sempat disampaikan.",-6,-2));
        return a;
    }
    public Result chooseDate(String choiceId){
        if(state.activeDate.isEmpty())return no("Belum ada kencan aktif.");
        Choice c=find(dateChoices(),choiceId);
        if(c==null)return no("Pilihan tidak dikenal.");
        state.trust=clamp(state.trust+c.trustChange);
        state.affection=clamp(state.affection+c.affectionChange);
        state.datesCompleted=Math.min(9999,state.datesCompleted+1);
        if("listen".equals(c.id))state.careActions=Math.min(9999,state.careActions+1);
        state.tokens=Math.min(999,state.tokens+2);
        state.lastDate=state.activeDate;
        state.lastDateChoice=c.id;
        state.dateHistory.add(state.activeDate+":"+c.id);trim(state.dateHistory);
        state.lastDateDay=state.day;
        state.activeDate="";
        log("Hari "+state.day+": "+state.lastDate+" - "+c.label);
        return yes(c.response+" (+2 token)");
    }
    public boolean hasDateChoice(String choice){
        if(choice==null)return false;
        for(String s:state.dateHistory)if(s.endsWith(":"+choice))return true;
        return false;
    }
    public List<Choice> dialogueChoices(){
        if(!state.activeDate.isEmpty()||state.lastDialogueDay>=state.day)return Collections.emptyList();
        ArrayList<Choice> a=new ArrayList<>();
        if(state.trust>=70)a.add(new Choice("honest","Bicara soal masa depan",partner()+" tersenyum mendengarnya.",4,4));
        else a.add(new Choice("honest","Cerita tentang kekhawatiran",partner()+" menghargai keterbukaanmu.",6,2));
        if("rush".equals(state.lastDateChoice))a.add(new Choice("repair","Minta maaf karena terburu-buru",partner()+" menerima permintaan maafmu.",6,3));
        if(hasDateChoice("plan"))a.add(new Choice("memory","Ingat rencana sebelumnya",partner()+" senang kamu masih ingat.",2,5));
        a.add(new Choice("comfort","Tanyakan perasaan pasangan",partner()+" merasa didengarkan.",3,3));
        a.add(new Choice("avoid","Alihkan pembicaraan","Percakapan berakhir singkat.",-4,-1));
        return a;
    }
    public Result chooseDialogue(String id){
        Choice c=find(dialogueChoices(),id);
        if(c==null)return no("Dialog sudah selesai atau pilihan tidak ada.");
        state.trust=clamp(state.trust+c.trustChange);state.affection=clamp(state.affection+c.affectionChange);
        state.lastDialogueDay=state.day;
        if("comfort".equals(c.id))state.careActions=Math.min(9999,state.careActions+1);
        log("Hari "+state.day+": dialog - "+c.label);
        return yes(c.response);
    }
    public Result giveGift(String id){
        if(!state.activeDate.isEmpty())return no("Selesaikan kencan dahulu.");
        Gift g=null;for(Gift x:GIFTS)if(x.id.equals(id))g=x;
        if(g==null)return no("Hadiah tidak dikenal.");
        if(state.giftsGiven.contains(id))return no("Hadiah ini sudah diberikan.");
        if(state.trust<g.minTrust||state.datesCompleted<g.minDates)return no("Persyaratan hadiah belum terpenuhi.");
        if(state.tokens<g.tokenCost)return no("Token kenangan belum cukup.");
        state.tokens-=g.tokenCost;state.giftsGiven.add(id);
        state.trust=clamp(state.trust+g.trustChange);state.affection=clamp(state.affection+g.affectionChange);
        log("Hari "+state.day+": hadiah "+g.name+" untuk "+partner());
        return yes(partner()+" menerima "+g.name+" dengan senyum.");
    }
    public Result makePromise(String id){
        if(!state.activeDate.isEmpty())return no("Selesaikan kencan dahulu.");
        if(!PROMISES.containsKey(id))return no("Janji tidak dikenal.");
        if(promise(id)!=null)return no("Janji sudah tercatat.");
        PromiseRecord p=new PromiseRecord(id,Math.min(9999,state.day+2));
        p.baseDates=state.datesCompleted;p.baseCare=state.careActions;p.baseGifts=state.giftsGiven.size();
        state.promises.add(p);log("Hari "+state.day+": berjanji "+PROMISES.get(id));
        return yes("Tepati sebelum akhir hari "+p.dueDay+".");
    }
    public Result fulfillPromise(String id){
        PromiseRecord p=promise(id);
        if(p==null||!"PENDING".equals(p.status)||state.day>p.dueDay)return no("Janji tidak dapat dipenuhi lagi.");
        if("on_time".equals(id)&&state.datesCompleted<=p.baseDates)return no("Selesaikan satu kencan dahulu.");
        if("listen".equals(id)&&state.careActions<=p.baseCare)return no("Dengarkan pasangan terlebih dahulu.");
        if("remember".equals(id)&&state.giftsGiven.size()<=p.baseGifts)return no("Berikan hadiah baru dahulu.");
        p.status="FULFILLED";state.trust=clamp(state.trust+8);state.affection=clamp(state.affection+3);
        state.tokens=Math.min(999,state.tokens+1);log("Hari "+state.day+": menepati janji "+id);
        return yes("Janji ditepati. Kepercayaan meningkat.");
    }
    private PromiseRecord promise(String id){for(PromiseRecord p:state.promises)if(p.id.equals(id))return p;return null;}
    public Moment moment(String id){for(Moment m:MOMENTS)if(m.id.equals(id))return m;return null;}
    public List<Moment> availableMoments(){
        if(!state.activeDate.isEmpty())return Collections.emptyList();
        ArrayList<Moment> list=new ArrayList<>();
        for(Moment m:MOMENTS){
            if(state.resolvedMoments.contains(m.id)||state.trust<m.minTrust||state.datesCompleted<m.minDates)continue;
            if(!"both".equals(m.route)&&!route.equals(m.route))continue;
            if("rain_together".equals(m.id)&&!hasDateChoice("listen"))continue;
            if("future_plan".equals(m.id)&&!hasDateChoice("plan"))continue;
            list.add(m);
        }
        return list;
    }
    public List<Choice> momentChoices(String momentId){
        if(!momentAvailable(momentId))return Collections.emptyList();
        ArrayList<Choice> a=new ArrayList<>();
        if("rain_together".equals(momentId)) {
            a.add(new Choice("share","Payungi "+partner(),"Kalian pulang bersama melewati hujan.",4,6));
            a.add(new Choice("wait","Tunggu hujan reda","Waktu menunggu menjadi momen hangat.",2,4));
        }else if("future_plan".equals(momentId)){
            a.add(new Choice("plan","Susun rencana bersama","Kalian memilih satu mimpi untuk diwujudkan.",5,7));
            a.add(new Choice("dream","Nikmati mimpi hari ini","Kalian menikmati kebersamaan tanpa tekanan.",2,5));
        }else{
            a.add(new Choice("share","Bagikan dengan tulus",partner()+" terharu dan tersenyum.",5,7));
            a.add(new Choice("keep","Simpan sebagai kejutan","Momen ini menjadi rahasia kecil kalian.",1,3));
        }
        return a;
    }
    public Result resolveMoment(String momentId,String choiceId){
        if(!momentAvailable(momentId))return no("Momen terkunci atau sudah selesai.");
        Choice c=find(momentChoices(momentId),choiceId);
        if(c==null)return no("Pilihan tidak valid.");
        state.resolvedMoments.add(momentId);
        state.trust=clamp(state.trust+c.trustChange);state.affection=clamp(state.affection+c.affectionChange);
        log("Hari "+state.day+": "+momentId+" - "+c.label);
        return yes(c.response);
    }
    private boolean momentAvailable(String id){for(Moment m:availableMoments())if(m.id.equals(id))return true;return false;}
    public boolean isReadyForSharedFinalChapter(){
        int completed=0;for(PromiseRecord p:state.promises)if("FULFILLED".equals(p.status))completed++;
        return state.datesCompleted>=3&&state.trust>=55&&completed>=1;
    }
    private void log(String msg){state.journal.add(msg);trim(state.journal);}
    private static void trim(ArrayList<String> list){while(list.size()>MAX_LOG)list.remove(0);}
    private static Choice find(List<Choice> list,String id){for(Choice c:list)if(c.id.equals(id))return c;return null;}
    private static int clamp(int n){return Math.max(0,Math.min(100,n));}
    private static Result yes(String s){return new Result(true,s);}
    private static Result no(String s){return new Result(false,s);}
    private static boolean validScene(String id){for(Scene s:SCENES)if(s.id.equals(id))return true;return false;}
    private static boolean validGift(String id){for(Gift g:GIFTS)if(g.id.equals(id))return true;return false;}
    private static boolean validMoment(String id){for(Moment m:MOMENTS)if(m.id.equals(id))return true;return false;}
    /** Defensive deep copy for missing fields, bad numeric values and future save extensions. */
    private static Snapshot sanitize(Snapshot old){
        Snapshot s=new Snapshot();
        s.schema=SCHEMA;s.route=old.route;
        s.day=Math.max(1,Math.min(9999,old.day));
        s.trust=clamp(old.trust);s.affection=clamp(old.affection);
        s.tokens=Math.max(0,Math.min(999,old.tokens));
        s.datesCompleted=Math.max(0,Math.min(9999,old.datesCompleted));
        s.careActions=Math.max(0,Math.min(9999,old.careActions));
        s.lastDateDay=Math.max(0,Math.min(9999,old.lastDateDay));
        s.lastDialogueDay=Math.max(0,Math.min(9999,old.lastDialogueDay));
        s.lastDate=validScene(old.lastDate)?old.lastDate:"";
        s.activeDate=validScene(old.activeDate)?old.activeDate:"";
        s.lastDateChoice="listen".equals(old.lastDateChoice)||"plan".equals(old.lastDateChoice)||"rush".equals(old.lastDateChoice)?old.lastDateChoice:"";
        if(old.giftsGiven!=null)for(String id:old.giftsGiven)if(id!=null&&validGift(id)&&!s.giftsGiven.contains(id))s.giftsGiven.add(id);
        if(old.dateHistory!=null)for(String entry:old.dateHistory){
            if(entry==null)continue;int split=entry.indexOf(':');
            if(split<=0||!validScene(entry.substring(0,split)))continue;
            String c=entry.substring(split+1);
            if("listen".equals(c)||"plan".equals(c)||"rush".equals(c))s.dateHistory.add(entry);
            trim(s.dateHistory);
        }
        if(old.resolvedMoments!=null)for(String id:old.resolvedMoments)
            if(id!=null&&validMoment(id)&&!s.resolvedMoments.contains(id))s.resolvedMoments.add(id);
        if(old.promises!=null)for(PromiseRecord p:old.promises){
            if(p==null||!PROMISES.containsKey(p.id))continue;
            boolean duplicate=false;for(PromiseRecord existing:s.promises)if(existing.id.equals(p.id))duplicate=true;
            if(duplicate)continue;
            PromiseRecord cp=new PromiseRecord(p.id,Math.max(1,Math.min(9999,p.dueDay)));
            cp.baseCare=Math.max(0,Math.min(9999,p.baseCare));
            cp.baseDates=Math.max(0,Math.min(9999,p.baseDates));
            cp.baseGifts=Math.max(0,Math.min(4,p.baseGifts));
            cp.status="FULFILLED".equals(p.status)||"BROKEN".equals(p.status)?p.status:"PENDING";
            if("PENDING".equals(cp.status)&&s.day>cp.dueDay)cp.status="BROKEN";
            s.promises.add(cp);
        }
        if(old.journal!=null)for(String entry:old.journal){
            if(entry!=null)s.journal.add(entry.substring(0,Math.min(320,entry.length())));
            trim(s.journal);
        }
        return s;
    }
}
