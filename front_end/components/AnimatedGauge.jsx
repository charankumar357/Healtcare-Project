import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Platform } from 'react-native';
import Svg, { Path } from 'react-native-svg';
import Animated, {
    useSharedValue,
    useAnimatedProps,
    withTiming,
    Easing,
    interpolateColor,
} from 'react-native-reanimated';
import Colors from '../constants/Colors';

const AnimatedPath = Animated.createAnimatedComponent(Path);

// Gauge configuration
const RADIUS = 100;
const STROKE_WIDTH = 20;
const CIRCUMFERENCE = Math.PI * RADIUS;

export default function AnimatedGauge({ score, tier }) {
    // Shared value for animation (0 to 1)
    const progress = useSharedValue(0);

    useEffect(() => {
        // Animate from 0 to target score fraction over 1.2s
        progress.value = withTiming(score / 100, {
            duration: 1200,
            easing: Easing.out(Easing.cubic),
        });
    }, [score]);

    // Determine color based on tier
    const getTierColor = (t) => {
        switch (t) {
            case 'low': return Colors.low; // Green
            case 'moderate': return Colors.moderate; // Orange
            case 'high': return Colors.high; // Red
            case 'critical': return Colors.critical; // Dark Red
            default: return Colors.primary;
        }
    };

    const activeColor = getTierColor(tier);

    // On Web, Reanimated useAnimatedProps with SVG often crashes the render,
    // which aborts the router navigation silently.
    if (Platform.OS === 'web') {
        const staticDashoffset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
        return (
            <View style={styles.container}>
                <Svg width={RADIUS * 2 + STROKE_WIDTH} height={RADIUS + STROKE_WIDTH} viewBox={`0 0 ${RADIUS * 2 + STROKE_WIDTH} ${RADIUS + STROKE_WIDTH / 2}`}>
                    <Path
                        d={`M ${STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2} A ${RADIUS} ${RADIUS} 0 0 1 ${RADIUS * 2 + STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2}`}
                        stroke={Colors.border} strokeWidth={STROKE_WIDTH} strokeLinecap="round" fill="none"
                    />
                    <Path
                        d={`M ${STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2} A ${RADIUS} ${RADIUS} 0 0 1 ${RADIUS * 2 + STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2}`}
                        stroke={activeColor} strokeWidth={STROKE_WIDTH} strokeLinecap="round" fill="none"
                        strokeDasharray={CIRCUMFERENCE} strokeDashoffset={staticDashoffset}
                    />
                </Svg>
                <View style={styles.scoreContainer}>
                    <Text style={[styles.scoreText, { color: activeColor }]}>{score}</Text>
                </View>
            </View>
        );
    }

    // Native: Animate the strokeDashoffset to draw the arc
    const animatedProps = useAnimatedProps(() => {
        const dashoffset = CIRCUMFERENCE - progress.value * CIRCUMFERENCE;
        return {
            strokeDashoffset: dashoffset,
        };
    });

    return (
        <View style={styles.container}>
            {/* Semicircle SVG */}
            <Svg width={RADIUS * 2 + STROKE_WIDTH} height={RADIUS + STROKE_WIDTH} viewBox={`0 0 ${RADIUS * 2 + STROKE_WIDTH} ${RADIUS + STROKE_WIDTH / 2}`}>

                {/* Background track arc */}
                <Path
                    d={`M ${STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2} A ${RADIUS} ${RADIUS} 0 0 1 ${RADIUS * 2 + STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2}`}
                    stroke={Colors.border}
                    strokeWidth={STROKE_WIDTH}
                    strokeLinecap="round"
                    fill="none"
                />

                {/* Animated foreground arc */}
                <AnimatedPath
                    d={`M ${STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2} A ${RADIUS} ${RADIUS} 0 0 1 ${RADIUS * 2 + STROKE_WIDTH / 2} ${RADIUS + STROKE_WIDTH / 2}`}
                    stroke={activeColor}
                    strokeWidth={STROKE_WIDTH}
                    strokeLinecap="round"
                    fill="none"
                    strokeDasharray={CIRCUMFERENCE}
                    animatedProps={animatedProps}
                />
            </Svg>

            {/* Score Text in Center */}
            <View style={styles.scoreContainer}>
                <Text style={[styles.scoreText, { color: activeColor }]}>{score}</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        justifyContent: 'flex-end',
        height: RADIUS + STROKE_WIDTH,
        position: 'relative',
        marginTop: 24,
    },
    scoreContainer: {
        position: 'absolute',
        bottom: -10,
        alignItems: 'center',
    },
    scoreText: {
        fontSize: 56,
        fontWeight: 'bold',
    },
});
