from lib.window_arena import * 

from lib.winobj_ship import * 

from typing import List 

#update ship (this is where your code goes) 

def updateShipRishi(ship: Ship, powerUps: List[PowerUp], targets: List[Target]): 
    ship.setPlayerName("Rishi M") 
    def normalizeAngle(angle) : 
        if angle < 0 : 
            angle = 360+angle 
        return angle 
    heading = math.degrees(math.atan2(ship.dir[1],ship.dir[0])) 
    heading = normalizeAngle(heading) 
    def calculateAngle(pos1, pos2) : 
        dist = pos2-pos1 
        return math.degrees(math.atan2(dist[1],dist[0])) 
    def calculateDistance(pos1,pos2) : 
        dist = pos2-pos1 
        return math.sqrt(dist[0]*dist[0] + dist[1]*dist[1]) 
    def calculateClosest(items,abs) : 
        nearest = items[0] 
        for i in items : 
            if(calculateDistance(abs,i.pos) < calculateDistance(nearest.pos,abs)) : 
                nearest = i 
        return nearest 
    def turnTo(angle,heading) : 
        dist = heading - angle 
        dist = normalizeAngle (dist) 
        if dist >= 180 and 360-dist > 1: 
            ship.queueCommand(ShipCmd_ThrustRight(360-dist)) 
        elif dist < 180 and dist > 1: 
            ship.queueCommand(ShipCmd_ThrustLeft(dist)) 
    def predictLocation(target) : 
        angle = calculateAngle(ship.pos,target.pos) 
        angle = normalizeAngle(angle) 
        turnDist = normalizeAngle(heading -angle) 
        if(turnDist >= 180) : 
            turnDist = 360 - turnDist 
        turnTime = turnDist / ship.shipTurnSpeed 
        shotCoolDown = 1 - (time.time() - ship.timeLastShot) 
        if (shotCoolDown < 0) : 
            shotCoolDown = 0 
        if (shotCoolDown > turnTime): 
            turnTime = shotCoolDown 
        initialOffset = [target.vel[0] * turnTime, target.vel[1] * turnTime] 
        relativePos = (target.pos + initialOffset) - ship.pos 
        launchOffset = Ship.SHIP_SHELL_RADIUS 
        # set up equation dist from ship = distance that the bullet travels 
        # dist(target.vel*x + target.pos, ship.pos) = Ammo.SPEED * x 
        #r = relativePos, v = velocity, d = starting offset, s = ammo speed, t = time 
        # |r + vt| = d + st 
        # t^2(v^2 - s^2) + 2t(rv - ds) + (r^2-d^2) = 0 
        a = (target.vel[0]*target.vel[0] + target.vel[1]*target.vel[1]) - (Ammo.SPEED * Ammo.SPEED) 
        b = 2 * ((relativePos[0] * target.vel[0]+ relativePos[1] * target.vel[1]) - (Ammo.SPEED * launchOffset)) 
        c = (relativePos[0]*relativePos[0] + relativePos[1]*relativePos[1])- (launchOffset*launchOffset) 
        solutions = [] 
        if abs(a) < 0.00001 and abs(b) > 0.00001: 
            solutions.append(c * -1 / b)  
        else: 
            discriminant = (b * b) - 4 * (a * c) 
            if discriminant > 0: 
                root = math.sqrt(discriminant) 
                solutions.append((-b - root) / (2 * a)) 
                solutions.append((-b + root) / (2 * a)) 
            maxTime = ship.ammoMaxRange / Ammo.SPEED 
        validTimes = [] 
        for x in solutions : 
            if x > 0 and x < maxTime : 
                validTimes.append(x) 
        if not validTimes: 
            return None 
        flightTime = min(validTimes) 
        pos = relativePos + target.vel * flightTime 
        impactPos = target.pos + target.vel * (turnTime + flightTime) 
        if not (impactPos[0] < ship.window.minCoordinateX() or impactPos[0] > ship.window.maxCoordinateX() or impactPos[1] < ship.window.minCoordinateY() or impactPos[1] > ship.window.maxCoordinateY()): 
            return (flightTime, pos) 
    def moveTo(pos) : 
        angle = calculateAngle(ship.pos,pos) 
        turnTo(angle,heading) 
        ship.queueCommand(ShipCmd_Thrust(calculateDistance(pos,ship.pos))) 
    def powerUpValue(i) : 
        game:WindowArena = ship.window 
        if i.type=="1" : 
            return 1 
        elif i.type=="2" : 
            return 4 
        elif i.type=="3" : 
            return 6 
        elif i.type=="S" : 
            if(game.levelTime < 15) : 
                return 0 
            return 2 
        else : 
            if(game.levelTime < 15) : 
                return 0 
            return 0.25 
    def targetPowerUp(): 
        vectors = [] 
        for i in range(360): 
            angle = ((i/1.0)+90) % 360 
            angle = math.radians(angle) 
            x = math.cos(angle) 
            y = math.sin(angle) 
            dirVec = (x,y) 
            currentPos = ship.pos.copy() 
            score = 0 
            maxDist = 0 
            foundPowerUps = [] 
            for j in range(20) : 
                currentPos[0] += dirVec[0] 
                currentPos[1] += dirVec[1] 
                for k in powerUps : 
                    if calculateDistance(currentPos, k.pos) < 0.75 and k not in foundPowerUps: 
                        foundPowerUps.append(k) 
                        score += powerUpValue(k) 
                        maxDist = currentPos.copy() 
            if foundPowerUps.__len__() > 0 : 
                rotDist = abs(heading-math.degrees(angle)) 
                if rotDist > 180: 
                    rotDist = 360 - rotDist 
                rotTime = rotDist / ship.shipTurnSpeed 
                dist = calculateDistance(ship.pos,maxDist) / ship.shipMoveSpeed 
                vectors.append((maxDist,score / (rotTime + dist))) 
        if not vectors : 
            max = powerUps[0] 
            for i in powerUps: 
                if powerUpValue(max)/calculateDistance(max.pos,ship.pos) < powerUpValue(i) / calculateDistance(i.pos,ship.pos): 
                    max = i 
            return max.pos 
        max = vectors[0] 
        for i in vectors : 
            if i[1] > max[1]: 
                max = i 
        if (max[1] > 0) : 
            max[0][0] = max[0][0] 
            max[0][1] = max[0][1] 
            return max[0] 
        max = powerUps[0] 
        for i in powerUps: 
            if powerUpValue(max)/calculateDistance(max.pos,ship.pos) < powerUpValue(i) / calculateDistance(i.pos,ship.pos): 
                max = i 
        return max.pos 
    if ship.getOther() is not None : 
        other = ship.getOther() 
        if other.queuedCommands or other.activeCommand: 
            commands = [] 
            if other.queuedCommands : 
                commands = other.queuedCommands.copy() 
            if other.activeCommand is not None : 
                commands.append(other.activeCommand) 
            for i in commands: 
                if isinstance(i,ShipCmd_Shoot) : 
                    dir = i.dir 
                    angle = math.degrees(math.atan2(dir[1], dir[0])) 
                    angle = normalizeAngle(angle) 
                    angle1 = calculateAngle(other.pos,ship.pos) 
                    angle1 = normalizeAngle(angle1) 
                    if abs(angle-angle1) < 2.5: 
                        nearestPowerup = targetPowerUp() 
                        angle = calculateAngle(ship.pos,nearestPowerup) 
                        angle = normalizeAngle(angle) 
                        turnTo(angle,heading) 
                        ship.queueCommand(ShipCmd_Thrust(calculateDistance(ship.pos,nearestPowerup))) 
                        return 
    if (ship.ammo > 0): 
        possibleShots = [] 
        if (ship.getOther() is not None) : 
            predictedPos = predictLocation(ship.getOther()) 
            if (predictedPos is not None) : 
                if(abs(calculateAngle(ship.pos,predictedPos[1] + ship.pos)) < 60): 
                    possibleShots.append(predictedPos) 
        for i in targets: 
            predictedPos = predictLocation(i) 
            if predictedPos is not None: 
                possibleShots.append(predictedPos)  
        if possibleShots: 
            best = min(possibleShots, key=lambda entry: entry[0]) 
            ship.queueCommand(ShipCmd_Shoot(best[1])) 
    if(not ship.queuedCommands) : 
        nearestPowerup = targetPowerUp() 
        angle = calculateAngle(ship.pos,nearestPowerup) 
        angle = normalizeAngle(angle) 
        turnTo(angle,heading) 
        ship.queueCommand(ShipCmd_Thrust(calculateDistance(ship.pos,nearestPowerup))) 
    pass 

 


#################################################################################################### 

############################## DO NOT MODIFY METHODS BELOW THIS LINE ############################## 

########################## EXCEPT TO REMOVE TUTORIAL GAME CONFIG ARGUMENT ######################### 

#################################################################################################### 

WindowArena(userCode1 = updateShip1,

gameConfig = WindowArenaConfig.SPACE_BATTLE, 

windowTitle = "TSA@RHS: Space Battle!").runGameLoop() 

 