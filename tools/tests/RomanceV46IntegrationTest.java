import com.arlandsofia.olu.logic.romance.*;
import java.util.List;

/** Pure JDK17 smoke/regression tests; Android UI/build requires Android SDK. */
public final class RomanceV46IntegrationTest {
    private static int count=0;
    private static void check(boolean b,String msg){count++;if(!b)throw new AssertionError("Test "+count+": "+msg);}
    private static boolean choice(List<RomanceEngineV45.Choice> choices,String id){
        for(RomanceEngineV45.Choice x:choices)if(x.id.equals(id))return true;return false;
    }
    private static boolean moment(RomanceEngineV45 e,String id){
        for(RomanceEngineV45.Moment m:e.availableMoments())if(m.id.equals(id))return true;return false;
    }
    public static void main(String[] args){
        RomanceEngineV45 a=new RomanceEngineV45("arland"),s=new RomanceEngineV45("sofia");
        check(!a.partner().equals(s.partner()),"unique route perspective");
        check(a.canonEndingId().equals(s.canonEndingId()),"one canon ending");
        check(a.availableDates().size()>=4,"initial dates");
        check(a.startDate("library").ok,"start first date");
        check(!a.startDate("flower").ok,"no overlapping dates");
        check(a.chooseDate("listen").ok,"play dating choice");
        check(a.datesCompleted()==1,"date is counted once");
        check(!a.startDate("library").ok,"once per world day");
        check(!a.syncWorldDay(0).ok,"invalid day blocked");
        check(a.syncWorldDay(2).ok,"world day advances engine");
        // Main-story restore from an earlier day cannot duplicate a previous date.
        int oldTrust=a.trust(), oldDates=a.datesCompleted();
        check(!a.syncWorldDay(1).ok,"romance day must not roll backwards");
        check(a.day()==2 && a.trust()==oldTrust && a.datesCompleted()==oldDates,
                "backwards sync leaves all romance state unchanged");
        check(a.startDate("arcade").ok,"second date");
        check(a.chooseDate("plan").ok,"planning choice");
        check(a.hasDateChoice("plan")&&a.hasDateChoice("listen"),"records decisions");
        check(moment(a,"rain_together"),"shared rain event");
        check(moment(a,"arland_letter")&&!moment(a,"sofia_sketch"),"route exclusive event");
        check(a.resolveMoment("rain_together","share").ok,"shared moment resolution");
        check(!a.resolveMoment("rain_together","share").ok,"cannot farm special moment");
        check(a.giveGift("photo").ok,"gift gate works");
        check(!a.giveGift("photo").ok,"duplicate gift blocked");
        check(a.makePromise("listen").ok,"make care promise");
        check(!a.fulfillPromise("listen").ok,"promise needs actual care");
        check(a.chooseDialogue("comfort").ok,"care dialogue");
        check(a.fulfillPromise("listen").ok,"promise fulfilled by action");
        check(!a.fulfillPromise("listen").ok,"claim once");
        check(a.syncWorldDay(3).ok,"world day matches");
        check(a.startDate("city").ok&&a.chooseDate("plan").ok,"third date");
        check(moment(a,"future_plan"),"unlock future by planning");
        check(a.resolveMoment("future_plan","plan").ok,"future playable");
        check(a.isReadyForSharedFinalChapter(),"single shared final gate");
        check(a.journalEntries().size()>0,"journal events");
        int journalSize=a.journalEntries().size();
        a.journalEntries().clear();
        check(a.journalEntries().size()==journalSize,"journal defensive copy");
        RomanceEngineV45.Snapshot snapshot=a.snapshot();
        snapshot.trust=0;snapshot.giftsGiven.clear();
        check(a.trust()>0&&a.snapshot().giftsGiven.size()==1,"snapshot defensive copy");
        RomanceEngineV45 aRestore=new RomanceEngineV45("arland",a.snapshot());
        check(aRestore.trust()==a.trust()&&aRestore.datesCompleted()==3,"save roundtrip");
        RomanceEngineV45 other=new RomanceEngineV45("sofia",a.snapshot());
        check(other.trust()==60&&other.datesCompleted()==0,"route isolation");
        check(RomanceSlotKeysV45.namespace("arland",1).equals("olu-romance-v45-arland"),"slot1 backwards compatible");
        check(!RomanceSlotKeysV45.namespace("arland",1).equals(RomanceSlotKeysV45.namespace("arland",2)),"slot isolation");
        check(!RomanceSlotKeysV45.namespace("arland",2).equals(RomanceSlotKeysV45.namespace("sofia",2)),"route slot isolation");
        boolean failed=false;try{RomanceSlotKeysV45.namespace("arland",3);}catch(IllegalArgumentException e){failed=true;}
        check(failed,"out of range slot rejected");
        check(RomanceSavePolicyV45.acceptsExisting("arland",a.snapshot()),"valid saved data allowed");
        snapshot=a.snapshot();snapshot.schema=99;
        check(!RomanceSavePolicyV45.acceptsExisting("arland",snapshot),"future save protected");
        check(!RomanceSavePolicyV45.acceptsExisting("sofia",a.snapshot()),"cross route save protected");
        check(s.startDate("library").ok&&s.chooseDate("plan").ok,"second protagonist playable");
        check(moment(s,"sofia_sketch")&&!moment(s,"arland_letter"),"Sofia special scene");
        check(s.resolveMoment("sofia_sketch","share").ok,"Sofia special scene outcome");
        RomanceEngineV45 broken=new RomanceEngineV45("arland");
        check(broken.makePromise("remember").ok,"create promise");
        broken.syncWorldDay(4);
        check(broken.trust()==51,"broken promise penalty once");
        broken.syncWorldDay(5);
        check(broken.trust()==51,"no repeated penalty");
        check(!broken.syncWorldDay(1).ok && broken.day()==5 && broken.trust()==51,
                "restoring older world save must not remove already incurred penalty");
        RomanceEngineV45.Snapshot damaged=a.snapshot();damaged.journal=null;damaged.dateHistory=null;
        damaged.resolvedMoments=null;damaged.promises=null;damaged.giftsGiven=null;
        check(new RomanceEngineV45("arland",damaged).snapshot().journal!=null,"missing fields handled");
        System.out.println("PASS "+count+" Romance Simulation v4.6 assertions");
    }
}
