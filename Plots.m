%This is the plot of our partly-linear equations

light =   [  0,  50, 140, 190, 400, 500];
steer =   [-90, -90, -40,   0,  40,  80];
x = linspace(0,500,1000);
y = interp1(light,steer,x);
f1 = figure;
hold on
plot(light, steer,'o', x, y,'--');
title('Light Semi-Linear');
xlabel('Value of the light sensor');
ylabel('Steering value');
hold off
saveas(f1,'lightToSteeringPlot.png');

 
distance =   [2  ,  10,  13,  25,  40];
steerD =     [100,  30,   0, -60, -90];
x1 = linspace(2,40,1000);
y1 = interp1(distance,steerD,x1);
f2 = figure;
plot(distance, steerD,'o', x1, y1,'--');
title('Distance Semi-Linear');
xlabel('Value of the distance sensor');
ylabel('Steering value');
saveas(f2,'distanceToSteeringPlot.png');