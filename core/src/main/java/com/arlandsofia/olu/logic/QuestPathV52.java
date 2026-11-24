package com.arlandsofia.olu.logic;

import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

/**
 * v5.2 obstacle-aware quest compass. A* routes around actual map collision,
 * including dynamic gates and 2.5D terrace boundaries. Runs periodically,
 * not once per render frame. Quest target coordinates never change here.
 */
public final class QuestPathV52 {
    private QuestPathV52() {}
    private static final int CELL = 18;
    private static final int[] DX={1,-1,0,0}, DY={0,0,1,-1};
    private static final class Node implements Comparable<Node> {
        final int at; final float score;
        Node(int at,float score){this.at=at;this.score=score;}
        @Override public int compareTo(Node n){return Float.compare(score,n.score);}
    }
    public static final class Result {
        public final boolean found;
        public final float nextX,nextY;
        public final int estimatedSteps;
        Result(boolean ok,float x,float y,int steps){found=ok;nextX=x;nextY=y;estimatedSteps=steps;}
    }

    public static Result route(MapDb.Area area,float px,float py,float targetX,float targetY,float reachRadius) {
        if(area==null || area.blocked(px,py))return new Result(false,px,py,0);
        int cols=Math.max(1,(int)Math.ceil(area.w/CELL)),rows=Math.max(1,(int)Math.ceil(area.h/CELL));
        int n=cols*rows;
        float goalDist=Math.max(20f,reachRadius-7f);
        if(distance(px,py,targetX,targetY)<=goalDist)return new Result(true,px,py,0);
        int sx=Math.min(cols-1,Math.max(0,(int)(px/CELL)));
        int sy=Math.min(rows-1,Math.max(0,(int)(py/CELL)));
        // Grid samples can land on a prop edge despite legal continuous player coordinates.
        int start=-1;float startDistance=Float.POSITIVE_INFINITY;
        for(int y=Math.max(0,sy-2);y<=Math.min(rows-1,sy+2);y++)
            for(int x=Math.max(0,sx-2);x<=Math.min(cols-1,sx+2);x++){
                float cx=(x+.5f)*CELL,cy=(y+.5f)*CELL;
                if(area.blocked(cx,cy))continue;
                float d=distance(px,py,cx,cy);
                if(d<startDistance){startDistance=d;start=y*cols+x;}
            }
        if(start<0)return new Result(false,px,py,0);
        float[] cost=new float[n];Arrays.fill(cost,Float.POSITIVE_INFINITY);
        int[] previous=new int[n];Arrays.fill(previous,-1);
        boolean[] closed=new boolean[n];
        PriorityQueue<Node> open=new PriorityQueue<>();
        cost[start]=0f;
        open.add(new Node(start,distance(px,py,targetX,targetY)));
        int goal=-1;
        while(!open.isEmpty()) {
            int at=open.poll().at;
            if(closed[at])continue;
            closed[at]=true;
            int x=at%cols,y=at/cols;
            float wx=(x+.5f)*CELL,wy=(y+.5f)*CELL;
            if(distance(wx,wy,targetX,targetY)<=goalDist){goal=at;break;}
            for(int k=0;k<4;k++){
                int nx=x+DX[k],ny=y+DY[k];
                if(nx<0||ny<0||nx>=cols||ny>=rows)continue;
                int to=ny*cols+nx;
                if(closed[to])continue;
                float tx=(nx+.5f)*CELL,ty=(ny+.5f)*CELL;
                if(area.blocked(tx,ty)||!ElevationV50.canStep(area.terraces,wx,wy,tx,ty))continue;
                float ng=cost[at]+CELL;
                if(ng>=cost[to])continue;
                cost[to]=ng;previous[to]=at;
                open.add(new Node(to,ng+distance(tx,ty,targetX,targetY)));
            }
        }
        if(goal<0)return new Result(false,px,py,0);
        int step=goal;
        while(previous[step]>=0 && previous[step]!=start)step=previous[step];
        float firstX=(step%cols+.5f)*CELL,firstY=(step/cols+.5f)*CELL;
        return new Result(true,firstX,firstY,Math.max(1,Math.round(cost[goal]/16f)));
    }

    public static QuestCompass.Hint hint(MapDb.Area area,float x,float y,
                                          List<QuestDb.Interactable> candidates,String route) {
        QuestCompass.Hint direct=QuestCompass.nearest(x,y,candidates,route);
        if(direct==null||direct.reachable || area==null)return direct;
        QuestDb.Interactable best=null;
        float min=Float.POSITIVE_INFINITY;
        for(QuestDb.Interactable it:candidates){
            if(it==null || !it.forRoute(route))continue;
            float d=distance(x,y,it.x,it.y);
            if(d<min){best=it;min=d;}
        }
        if(best==null)return direct;
        if(clearLine(area,x,y,best.x,best.y) &&
                ElevationV50.canStep(area.terraces,x,y,best.x,best.y))return direct;
        Result path=route(area,x,y,best.x,best.y,best.r);
        if(!path.found)return new QuestCompass.Hint("cari jalur aman",direct.distance,direct.label,false,true);
        return new QuestCompass.Hint(QuestCompass.direction(path.nextX-x,path.nextY-y),
                path.estimatedSteps,direct.label,false,true);
    }

    private static boolean clearLine(MapDb.Area a,float x,float y,float tx,float ty) {
        float d=distance(x,y,tx,ty);
        int segments=Math.max(1,(int)Math.ceil(d/10f));
        for(int i=1;i<segments;i++){
            float f=(float)i/segments;
            if(a.blocked(x+(tx-x)*f,y+(ty-y)*f))return false;
        }
        return true;
    }
    private static float distance(float x,float y,float a,float b){
        float dx=x-a,dy=y-b;return (float)Math.sqrt(dx*dx+dy*dy);
    }
}
