# rstCA_v9.3.py
# Description: CA simulation platform using raster dataset (0-1 sim)
# Requirements: ArcGIS 9.3 (or above) with spatial analysis extensions
# Run this tool in IDLE of Python
# Author: Ying LONG, longying1980@gmail.com, Tsinghua University&BICP
# All right reserved, please do not ditribute it without author's permission
# Updated Date: 2012-12-24

import sys, string, random, os, time, arcgisscripting
gp = arcgisscripting.create()
gp.OverwriteOutput = 1

try:
    gp.Workspace = r"G:\BUDEM_JJJ\sim"
    logFile = r"G:\BUDEM_JJJ\sim\Result.mdb\LOG"
    loops = 1

    steps = 300          # maximum iterations
    alfa = 2
    k = 20.0             # random item
    inThreshold = 0.9999

    fm_obs = "p_plan"    # Select the form to be compared (planned form in most cases)
    fm_start = "urban_2010" # Land at t=0
    fm_extent = "full"   # Study area
    eclusive = ""        # eclusive layer "Constrain1", if null, then no eclusive

    total = 40000        # the total developed cell expected

    w0=0  #Constant
    w1=1  #Beijing center
    w2=1  #Tianjin Shijiazhuang centers
    w3=1  #Other centers
    w4=2  #railways
    w5=4  #highways
    w6=2  #national roads
    w7=1  #provincial roads
    w8=0  #airport 2
    w9=0  #sjtl
    wN0=0.2 #neighbor 0.2

    r1="f_ctr_bj"
    r2="f_ctr_tjsjz"
    r3="f_ctr_other"
    r4="f_railk2007"
    r5="f_r_hig2007"
    r6="f_r_nat2007"
    r7="f_r_pro2007"
    r8="f_air2"
    r9="f_r_sjtl"

    gp.CheckOutExtension("Spatial")
    # Delete former log
    cur = gp.UpdateCursor(logFile)
    row = cur.Next()
    while row:
        cur.DeleteRow(row)
        row = cur.Next()
    del row, cur
    print("Former log records deleted")
    
    # Delete former outputs and suit
    rsList = gp.ListRasters("ld*", "GRID")
    rs = rsList.Next()
    while rs:
        gp.delete(rs)
        print (rs + " deleted")
        rs = rsList.Next()
    del rs,rsList
    if gp.exists("suit"):
        gp.delete("suit")
        print ("suit deleted")
    gp.RefreshCatalog(gp.Workspace)

    gp.ZonalStatisticsAsTable_sa(fm_extent, "Value", fm_start, "zonestats.dbf", "DATA")
    # gp.ZonalStatisticsAsTable_sa(inRaster1, "Value", inRaster2, outTable, "DATA")
    
    cur = gp.SearchCursor("zonestats.dbf")
    row = cur.next()
    numStart0 = int(row.SUM)
    del cur,row
    gp.RefreshCatalog(gp.Workspace)
    gp.delete("zonestats.dbf")
    gp.RefreshCatalog(gp.Workspace)

    # Calculate suit
    expr = str(w0)+" + "+str(w1)+" * "+r1+" + "+str(w2)+" * "+r2+" + "+str(w3)+" * "+r3+" + "+str(w4)+" * "+r4
    expr = expr+" + "+str(w5)+" * "+r5+" + "+str(w6)+" * "+r6+" + "+str(w7)+" * "+r7+" + "+str(w8)+" * "+r8
    expr = expr+" + "+str(w9)+" * "+r9
    gp.SingleOutputMapAlgebra_sa(expr, "suit")
    gp.RefreshCatalog(gp.Workspace)
    print(expr)

    startT = time.time()
    alfa0 = alfa
    for j in range(loops):
        if not(loops==1):
            print ("Loop ID is: " + str(j + 0) + "-------------------------------------")
            alfa = alfa0
            wN = N0 + dtN*(j)
            print("wN = " + str(wN))
        else:
            wN = wN0
        
        for i in range(steps):
            print ("Iteration starts: " + str(i + 1) + "------------------------")
            # Delete all land* rasters in output directory
            rsList = gp.ListRasters("land*", "GRID")
            rs = rsList.Next()
            while rs:
                gp.delete(rs)
                rs = rsList.Next()
            del rs,rsList
            gp.RefreshCatalog(gp.Workspace)

            if i == 0:
                inFC = fm_start
                numStart = numStart0
            else:
                inFC = "ld" + str(i)
                numStart = numEnd
            print ("numStart = " + str(numStart))

            # rN calculate
            rN_t = "land_nt"
            InNeighborhood = "RECTANGLE 3 3 CELL"
            gp.FocalStatistics_sa(inFC, rN_t, InNeighborhood, "SUM", "DATA")
            gp.RefreshCatalog(gp.Workspace)
            rN = "( " + rN_t + " - " + inFC + " ) / 8"
            
            # p0 calculate
            expr = " suit + " + str(wN) + " * " + rN
            # p1 calculate
            expr = " 1 / ( 1 + exp ( -1 * ( " + expr + " ) ) )"
            expr = "( 1 - " + inFC + " ) * " + expr
            gp.SingleOutputMapAlgebra_sa(expr, "land_p1")
            # cal maximum of p1
            gp.ZonalStatisticsAsTable_sa(fm_extent, "Value", "land_p1", "zonestats.dbf", "DATA")
            cur = gp.SearchCursor("zonestats.dbf")
            row = cur.next()
            pMax = row.MAX
            del cur,row
            gp.RefreshCatalog(gp.Workspace)
            gp.delete("zonestats.dbf")
            gp.RefreshCatalog(gp.Workspace)

            # p2 calculate
            expr = " exp ( " + str(alfa) + " * ( " + " land_p1 " + " / " + str(pMax) + " - 1) "
            expr = expr + " * ( 1 + ( rand() - 0.5 ) / " + str(k) + " )"  # RI item
            expr = expr + " )"
            
            ########difference START
            expr = expr + " - " + str(inThreshold) + " "
            gp.SingleOutputMapAlgebra_sa(expr, "land_p2")
            gp.RefreshCatalog(gp.Workspace)
            gp.GreaterThanEqual_sa("land_p2", 0, "land_R")
            gp.RefreshCatalog(gp.Workspace)
                  
            ########difference END
            outFC = "ld" + str(i+1)
            if eclusive == "":
                gp.BooleanOr_sa("land_R", inFC, "land_tmp1")
                gp.RefreshCatalog(gp.Workspace)
            else:
                gp.BooleanOr_sa("land_R", inFC, "land_tmp")
                gp.RefreshCatalog(gp.Workspace)
                gp.BooleanAnd_sa("land_tmp", eclusive, "land_tmp1")
                gp.RefreshCatalog(gp.Workspace)

            gp.Times_sa("land_tmp1",fm_extent,outFC)
            gp.RefreshCatalog(gp.Workspace)

            # calculate Kappa and GOF
            gp.ZonalStatisticsAsTable_sa(fm_obs, "Value", outFC, "zonestats.dbf", "DATA") # former problem here
            gp.RefreshCatalog(gp.Workspace)
            cur = gp.SearchCursor("zonestats.dbf")
            row = cur.next()
            x11 = int(row.COUNT)-int(row.SUM)
            x12 = int(row.SUM)
            row = cur.next()
            x21 = int(row.COUNT)-int(row.SUM)
            x22 = int(row.SUM)
            del cur,row
            gp.delete("zonestats.dbf")
            gp.RefreshCatalog(gp.Workspace)

            xT = float(x11+x12+x21+x22)
            x1 = x11 + x12
            x2 = x21 + x22
            x_1 = x11 + x21
            x_2 = x12 + x22
            Kappa = float((xT*(x11+x22)-x1*x_1-x2*x_2)/(xT*xT-x1*x_1-x2*x_2))*100.0
            GOF = float((x11+x22)/xT)*100.0
            print("Kappa = " + str(Kappa))
            print("GOF = " + str(GOF))
            
            # Calculate total built-up
            numEnd = x12+x22
            print ("numEnd = " + str(numEnd))
            numCHG = numEnd - numStart
            print ("numCHG = " + str(numCHG))

            # change alfa according to numGap
            if numCHG < 200: # var
                alfa = alfa * 0.9
                print ("alfa = " + str(alfa))
           
            cur = gp.InsertCursor(logFile)
            row = cur.NewRow()
            row.LoopID = j + 1
            row.StepID = i + 1
            row.xN = wN
            row.numStart = numStart
            row.numEnd = numEnd
            row.numCHG = numCHG
            row.alfa = alfa
            row.GOF = GOF
            row.Kappa = Kappa
            cur.InsertRow(row)
            print("New log record inserted")

            numStart = numEnd
            print ("Iteration finished: " + str(i + 1))

            if numEnd > total:
                print("Breaking.....................")
                break
            
        # Delete no use rasters in the directory
        rsList = gp.ListRasters("land*", "GRID")
        rs = rsList.Next()
        while rs:
            gp.delete(rs)
            print(rs + " deleted")
            rs = rsList.Next()
        del rs,rsList
        gp.RefreshCatalog(gp.Workspace)

    ####MonoLoop END
    gp.CheckInExtension("Spatial")
    endT = time.time()
    print("Total calculation time is " + str(long(endT-startT)) + " seconds")
    print("rstCA finished now")

except:
    # Print error message if an error occurs
    gp.GetMessages()
