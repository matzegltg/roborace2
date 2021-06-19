%This is the plot of our partly-linear equations


val =   [  0,  10,  13,  17,  25,  40]
steer = [100,  30,   0, -40, -75, -90]
x = linspace(val(1),val(end),1000);
y = interp1(val,steer,x);
f1 = figure;
hold on
plot(val, steer,'o', x, y,'--');
title('Light Semi-Linear');
xlabel('Light sensor');
ylabel('Steering value');
hold off
saveas(f1,'lightToSteeringPlot.png');

 
valD = [  0, 150, 450, 600]
steer= [-90, -90,  50,  70]
x1 = linspace(0,600,1000);
y1 = interp1(valD,steer,x1);
f2 = figure;
plot(valD, steer,'o', x1, y1,'--');
title('Distance Semi-Linear');
xlabel('Distance sensor');
ylabel('Steering value');
saveas(f2,'distanceToSteeringPlot.png');